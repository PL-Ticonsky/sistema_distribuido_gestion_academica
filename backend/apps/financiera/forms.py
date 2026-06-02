import uuid
from decimal import Decimal

from django import forms
from django.utils import timezone

from apps.academica.models import Estudiante
from apps.accounts.roles import get_user_roles
from apps.accounts.scope import (
    get_administrative_faculty_ids,
    get_program_ids_for_faculties,
    get_visible_program_ids,
    get_visible_student_ids,
    is_superadmin,
)
from apps.financiera.models import Matricula, Recibo, TarifaMatricula


def user_can_manage_financial(user):
    roles = set(get_user_roles(user))
    return is_superadmin(user) or "administrativo" in roles


def get_financial_program_ids(user):
    if is_superadmin(user):
        return None

    program_ids = set(get_visible_program_ids(user, include_student=True) or [])
    program_ids.update(
        get_program_ids_for_faculties(get_administrative_faculty_ids(user))
    )
    return list(program_ids)


def get_financial_student_queryset(user):
    queryset = Estudiante.objects.select_related("usuario", "programa_academico")
    student_ids = get_visible_student_ids(user)
    if student_ids is None:
        return queryset
    return queryset.filter(id_estudiante__in=student_ids)


def get_financial_tarifa_queryset(user):
    queryset = TarifaMatricula.objects.select_related(
        "programa_academico",
        "periodo_academico",
    )
    program_ids = get_financial_program_ids(user)
    if program_ids is None:
        return queryset
    return queryset.filter(programa_academico_id__in=program_ids)


def active_or_finalized_matriculas_count(estudiante):
    return Matricula.objects.filter(
        recibo__estudiante=estudiante,
        estado_matricula__in=[
            Matricula.EstadoMatricula.ACTIVA,
            Matricula.EstadoMatricula.FINALIZADA,
        ],
    ).count()


def validate_matricula_limit(estudiante):
    used = active_or_finalized_matriculas_count(estudiante)
    if used >= estudiante.limite_matriculas:
        raise forms.ValidationError(
            "El estudiante alcanzo el limite de matriculas permitido.",
        )


class TarifaMatriculaForm(forms.ModelForm):
    class Meta:
        model = TarifaMatricula
        fields = [
            "programa_academico",
            "periodo_academico",
            "valor_matricula",
            "fecha_limite_ordinaria",
            "fecha_limite_extraordinaria",
            "estado",
        ]
        labels = {
            "programa_academico": "Programa academico",
            "periodo_academico": "Periodo academico",
            "valor_matricula": "Valor matricula",
            "fecha_limite_ordinaria": "Fecha limite ordinaria",
            "fecha_limite_extraordinaria": "Fecha limite extraordinaria",
        }
        widgets = {
            "fecha_limite_ordinaria": forms.DateInput(attrs={"type": "date"}),
            "fecha_limite_extraordinaria": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        program_ids = get_financial_program_ids(user)
        if program_ids is not None:
            self.fields["programa_academico"].queryset = self.fields[
                "programa_academico"
            ].queryset.filter(id_programa_academico__in=program_ids)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned_data = super().clean()
        program = cleaned_data.get("programa_academico")
        period = cleaned_data.get("periodo_academico")
        value = cleaned_data.get("valor_matricula")
        ordinary = cleaned_data.get("fecha_limite_ordinaria")
        extraordinary = cleaned_data.get("fecha_limite_extraordinaria")

        if value is not None and value < Decimal("0"):
            raise forms.ValidationError("El valor de matricula no puede ser negativo.")

        if ordinary and extraordinary and extraordinary < ordinary:
            raise forms.ValidationError(
                "La fecha extraordinaria no puede ser anterior a la ordinaria.",
            )

        if program and period:
            duplicate = TarifaMatricula.objects.filter(
                programa_academico=program,
                periodo_academico=period,
            )
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise forms.ValidationError(
                    "Ya existe una tarifa para este programa y periodo.",
                )

        return cleaned_data

    def save(self, commit=True):
        tarifa = super().save(commit=False)
        if not tarifa.pk:
            tarifa.id_tarifa_matricula = uuid.uuid4()
        if commit:
            tarifa.save()
        return tarifa


class ReciboForm(forms.ModelForm):
    class Meta:
        model = Recibo
        fields = [
            "estudiante",
            "tarifa_matricula",
            "estado_pago",
            "fecha_pago",
            "valor_pagado",
            "metodo_pago",
            "extras",
        ]
        labels = {
            "tarifa_matricula": "Tarifa de matricula",
            "estado_pago": "Estado de pago",
            "fecha_pago": "Fecha de pago",
            "valor_pagado": "Valor pagado",
            "metodo_pago": "Metodo de pago",
        }
        widgets = {
            "fecha_pago": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["estudiante"].queryset = get_financial_student_queryset(user)
        self.fields["tarifa_matricula"].queryset = get_financial_tarifa_queryset(user)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("estudiante")
        tarifa = cleaned_data.get("tarifa_matricula")
        payment_state = cleaned_data.get("estado_pago")
        paid_value = cleaned_data.get("valor_pagado")
        extras = cleaned_data.get("extras")

        if self.instance.pk and self.instance.estado_pago == Recibo.EstadoPago.ANULADO:
            raise forms.ValidationError(
                "No se puede pagar ni editar un recibo anulado.",
            )

        if (
            student
            and tarifa
            and student.programa_academico_id != tarifa.programa_academico_id
        ):
            raise forms.ValidationError(
                "La tarifa debe corresponder al programa del estudiante.",
            )

        if student and tarifa:
            duplicate = Recibo.objects.filter(
                estudiante=student,
                tarifa_matricula=tarifa,
            )
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise forms.ValidationError(
                    "Ya existe un recibo para este estudiante y tarifa.",
                )

        if paid_value is not None and paid_value < Decimal("0"):
            raise forms.ValidationError("El valor pagado no puede ser negativo.")

        if extras is not None and extras < Decimal("0"):
            raise forms.ValidationError("Los extras no pueden ser negativos.")

        if payment_state == Recibo.EstadoPago.PAGADO and paid_value is None:
            raise forms.ValidationError(
                "Un recibo pagado debe registrar el valor pagado.",
            )

        if payment_state != Recibo.EstadoPago.PAGADO:
            cleaned_data["fecha_pago"] = None
            cleaned_data["valor_pagado"] = None
            cleaned_data["metodo_pago"] = None

        return cleaned_data

    def save(self, commit=True):
        recibo = super().save(commit=False)
        if not recibo.pk:
            recibo.id_recibo = uuid.uuid4()
        if recibo.estado_pago == Recibo.EstadoPago.PAGADO and not recibo.fecha_pago:
            recibo.fecha_pago = timezone.localdate()
        if commit:
            recibo.save()
        return recibo


class MatriculaCreateForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ["recibo", "estado_matricula"]
        labels = {
            "estado_matricula": "Estado de matricula",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["recibo"].queryset = (
            Recibo.objects.select_related(
                "estudiante__usuario",
                "estudiante__programa_academico",
                "tarifa_matricula__periodo_academico",
            )
            .filter(
                id_recibo__in=get_financial_recibo_ids(user),
                estado_pago=Recibo.EstadoPago.PAGADO,
                matricula__isnull=True,
            )
            .distinct()
        )
        self.fields["estado_matricula"].choices = [
            (Matricula.EstadoMatricula.PENDIENTE, "Pendiente"),
            (Matricula.EstadoMatricula.ACTIVA, "Activa"),
        ]
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned_data = super().clean()
        recibo = cleaned_data.get("recibo")
        state = cleaned_data.get("estado_matricula")
        if not recibo:
            return cleaned_data

        if recibo.estado_pago != Recibo.EstadoPago.PAGADO:
            raise forms.ValidationError(
                "Solo se puede crear matricula desde un recibo pagado.",
            )

        if Matricula.objects.filter(recibo=recibo).exists():
            raise forms.ValidationError("Este recibo ya tiene una matricula asociada.")

        if state == Matricula.EstadoMatricula.ACTIVA:
            validate_matricula_limit(recibo.estudiante)

        return cleaned_data

    def save(self, commit=True):
        matricula = super().save(commit=False)
        matricula.id_matricula = uuid.uuid4()
        if commit:
            matricula.save()
        return matricula


def get_financial_recibo_ids(user):
    queryset = Recibo.objects.all()
    if is_superadmin(user):
        return queryset.values_list("id_recibo", flat=True)

    student_ids = get_visible_student_ids(user)
    if not student_ids:
        return []
    return queryset.filter(estudiante_id__in=student_ids).values_list(
        "id_recibo",
        flat=True,
    )
