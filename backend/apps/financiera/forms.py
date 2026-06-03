from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.roles import get_user_roles
from apps.accounts.scope import is_superadmin
from apps.estructura.models import PeriodoAcademico, ProgramaAcademico
from apps.financiera.distributed_write import (
    anular_recibo,
    cancel_matricula,
    create_matricula,
    create_recibo,
    create_tarifa,
    deactivate_tarifa,
    update_matricula,
    update_recibo,
    update_tarifa,
)
from apps.financiera.models import MatriculaDetalle, Recibo, TarifaMatricula
from apps.reportes.choices import estudiante_labels
from apps.reportes.models import EstudianteDetalle

TARIFA_STATUS_CHOICES = (
    ("Activa", "Activa"),
    ("Inactiva", "Inactiva"),
)

RECIBO_STATUS_CHOICES = (
    ("Pendiente", "Pendiente"),
    ("Pagado", "Pagado"),
    ("Vencido", "Vencido"),
    ("Anulado", "Anulado"),
)

METODO_PAGO_CHOICES = (
    ("", "---------"),
    ("Efectivo", "Efectivo"),
    ("Tarjeta", "Tarjeta"),
    ("PSE", "PSE"),
    ("Transferencia", "Transferencia"),
    ("Consignacion", "Consignacion"),
)

MATRICULA_STATUS_CHOICES = (
    ("Pendiente", "Pendiente"),
    ("Activa", "Activa"),
    ("Finalizada", "Finalizada"),
    ("Cancelada", "Cancelada"),
)


def user_can_manage_financial(user):
    roles = set(get_user_roles(user))
    return is_superadmin(user) or "administrativo" in roles


class TarifaMatriculaForm(forms.Form):
    programa_academico = forms.ModelChoiceField(
        label="Programa academico",
        queryset=ProgramaAcademico.objects.none(),
    )
    periodo_academico = forms.ModelChoiceField(
        label="Periodo academico",
        queryset=PeriodoAcademico.objects.none(),
    )
    valor_matricula = forms.DecimalField(
        label="Valor matricula",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
    )
    fecha_limite_ordinaria = forms.DateField(
        label="Fecha limite ordinaria",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    fecha_limite_extraordinaria = forms.DateField(
        label="Fecha limite extraordinaria",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    estado = forms.ChoiceField(label="Estado", choices=TARIFA_STATUS_CHOICES)

    def __init__(self, *args, tarifa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tarifa = tarifa
        self.fields["programa_academico"].queryset = ProgramaAcademico.objects.order_by(
            "facultad__nombre_facultad",
            "nombre_programa",
        )
        self.fields["periodo_academico"].queryset = PeriodoAcademico.objects.order_by(
            "-fecha_inicio",
            "id_periodo_academico",
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        if tarifa is not None:
            self.fields["programa_academico"].initial = tarifa.programa_academico_id
            self.fields["periodo_academico"].initial = tarifa.periodo_academico_id
            self.fields["valor_matricula"].initial = tarifa.valor_matricula
            self.fields[
                "fecha_limite_ordinaria"
            ].initial = tarifa.fecha_limite_ordinaria
            self.fields[
                "fecha_limite_extraordinaria"
            ].initial = tarifa.fecha_limite_extraordinaria
            self.fields["estado"].initial = tarifa.estado

    def clean(self):
        cleaned_data = super().clean()
        program = cleaned_data.get("programa_academico")
        period = cleaned_data.get("periodo_academico")
        ordinary = cleaned_data.get("fecha_limite_ordinaria")
        extraordinary = cleaned_data.get("fecha_limite_extraordinaria")

        if ordinary and extraordinary and extraordinary < ordinary:
            raise ValidationError(
                "La fecha extraordinaria no puede ser anterior a la ordinaria.",
            )

        if program and period:
            duplicate = TarifaMatricula.objects.filter(
                programa_academico=program,
                periodo_academico=period,
            )
            if self.tarifa is not None:
                duplicate = duplicate.exclude(pk=self.tarifa.pk)
            if duplicate.exists():
                raise ValidationError(
                    "Ya existe una tarifa para este programa y periodo.",
                )

        return cleaned_data

    def save(self):
        data = self.cleaned_data
        kwargs = {
            "id_programa_academico": data["programa_academico"].pk,
            "id_periodo_academico": data["periodo_academico"].pk,
            "valor_matricula": data["valor_matricula"],
            "fecha_limite_ordinaria": data["fecha_limite_ordinaria"],
            "fecha_limite_extraordinaria": data["fecha_limite_extraordinaria"],
            "estado": data["estado"],
        }
        if self.tarifa is None:
            return create_tarifa(**kwargs)
        return update_tarifa(
            id_tarifa_matricula=self.tarifa.id_tarifa_matricula,
            **kwargs,
        )


class ReciboForm(forms.Form):
    id_estudiante = forms.ModelChoiceField(
        label="Estudiante",
        queryset=EstudianteDetalle.objects.none(),
    )
    tarifa_matricula = forms.ModelChoiceField(
        label="Tarifa de matricula",
        queryset=TarifaMatricula.objects.none(),
    )
    estado_pago = forms.ChoiceField(
        label="Estado de pago",
        choices=RECIBO_STATUS_CHOICES,
    )
    fecha_pago = forms.DateField(
        label="Fecha de pago",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    valor_pagado = forms.DecimalField(
        label="Valor pagado",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
    )
    metodo_pago = forms.ChoiceField(
        label="Metodo de pago",
        choices=METODO_PAGO_CHOICES,
        required=False,
    )
    extras = forms.DecimalField(
        label="Extras",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        initial=Decimal("0"),
    )

    def __init__(self, *args, recibo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.recibo = recibo
        self.fields["id_estudiante"].queryset = EstudianteDetalle.objects.order_by(
            "nombre_facultad",
            "nombre_programa",
            "estudiante",
        )
        self.fields["tarifa_matricula"].queryset = TarifaMatricula.objects.filter(
            estado="Activa",
        ).select_related("programa_academico", "periodo_academico")
        self.fields["id_estudiante"].label_from_instance = (
            lambda student: (
                f"{student.nombre_facultad} - {student.estudiante} "
                f"({student.nombre_programa})"
            )
        )
        self.fields["tarifa_matricula"].label_from_instance = (
            lambda tarifa: (
                f"{tarifa.programa_academico.nombre_programa} - "
                f"{tarifa.periodo_academico_id} - {tarifa.valor_matricula}"
            )
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        if recibo is not None:
            if recibo.tarifa_matricula_id:
                current_tarifa = TarifaMatricula.objects.filter(
                    pk=recibo.tarifa_matricula_id,
                )
                self.fields["tarifa_matricula"].queryset = (
                    current_tarifa | self.fields["tarifa_matricula"].queryset
                )
            self.fields["id_estudiante"].initial = recibo.id_estudiante
            self.fields["tarifa_matricula"].initial = recibo.tarifa_matricula_id
            self.fields["estado_pago"].initial = recibo.estado_pago
            self.fields["fecha_pago"].initial = recibo.fecha_pago
            self.fields["valor_pagado"].initial = recibo.valor_pagado
            self.fields["metodo_pago"].initial = recibo.metodo_pago or ""
            self.fields["extras"].initial = recibo.extras

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("id_estudiante")
        tarifa = cleaned_data.get("tarifa_matricula")
        state = cleaned_data.get("estado_pago")
        paid_value = cleaned_data.get("valor_pagado")
        method = cleaned_data.get("metodo_pago") or None

        if self.recibo is not None and self.recibo.estado_pago == "Anulado":
            raise ValidationError("No se puede editar un recibo anulado.")

        if student and tarifa:
            if student.id_facultad != tarifa.id_facultad:
                raise ValidationError(
                    "La tarifa debe pertenecer a la facultad del estudiante.",
                )
            if student.id_programa_academico != tarifa.programa_academico_id:
                raise ValidationError(
                    "La tarifa debe corresponder al programa del estudiante.",
                )
            duplicate = Recibo.objects.filter(
                id_estudiante=student.pk,
                tarifa_matricula=tarifa,
            )
            if self.recibo is not None:
                duplicate = duplicate.exclude(pk=self.recibo.pk)
            if duplicate.exists():
                raise ValidationError(
                    "Ya existe un recibo para este estudiante y tarifa.",
                )
        if state == "Pagado" and paid_value is None:
            raise ValidationError("Un recibo pagado debe registrar el valor pagado.")

        if state != "Pagado":
            cleaned_data["fecha_pago"] = None
            cleaned_data["valor_pagado"] = None
            cleaned_data["metodo_pago"] = None
        else:
            cleaned_data["metodo_pago"] = method
            if not cleaned_data.get("fecha_pago"):
                cleaned_data["fecha_pago"] = timezone.localdate()

        return cleaned_data

    def save(self):
        data = self.cleaned_data
        kwargs = {
            "id_estudiante": data["id_estudiante"].pk,
            "id_tarifa_matricula": data["tarifa_matricula"].pk,
            "fecha_pago": data["fecha_pago"],
            "valor_pagado": data["valor_pagado"],
            "metodo_pago": data["metodo_pago"],
            "estado_pago": data["estado_pago"],
            "extras": data["extras"],
        }
        if self.recibo is None:
            return create_recibo(**kwargs)
        return update_recibo(id_recibo=self.recibo.id_recibo, **kwargs)


class MatriculaForm(forms.Form):
    id_recibo = forms.ModelChoiceField(
        label="Recibo",
        queryset=Recibo.objects.none(),
    )
    estado_matricula = forms.ChoiceField(
        label="Estado de matricula",
        choices=MATRICULA_STATUS_CHOICES,
    )

    def __init__(self, *args, matricula=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.matricula = matricula
        recibos = Recibo.objects.filter(estado_pago="Pagado").select_related(
            "tarifa_matricula",
            "tarifa_matricula__programa_academico",
            "tarifa_matricula__periodo_academico",
        )
        if matricula is None:
            used = MatriculaDetalle.objects.values_list("id_recibo", flat=True)
            recibos = recibos.exclude(id_recibo__in=used)
        elif matricula.id_recibo:
            recibos = Recibo.objects.filter(pk=matricula.id_recibo) | recibos
        self.fields["id_recibo"].queryset = recibos.distinct()
        labels = estudiante_labels(
            self.fields["id_recibo"].queryset.values_list("id_estudiante", flat=True),
        )
        self.fields["id_recibo"].label_from_instance = (
            lambda recibo: (
                f"{labels.get(recibo.id_estudiante, recibo.id_estudiante)} - "
                f"{recibo.tarifa_matricula.programa_academico.nombre_programa} - "
                f"{recibo.tarifa_matricula.periodo_academico_id}"
            )
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        if matricula is not None:
            self.fields["id_recibo"].initial = matricula.id_recibo
            self.fields["estado_matricula"].initial = matricula.estado_matricula

    def clean(self):
        cleaned_data = super().clean()
        recibo = cleaned_data.get("id_recibo")
        if not recibo:
            return cleaned_data

        duplicate = MatriculaDetalle.objects.filter(id_recibo=recibo.pk)
        if self.matricula is not None:
            duplicate = duplicate.exclude(pk=self.matricula.pk)
        if duplicate.exists():
            raise ValidationError("Este recibo ya tiene una matricula asociada.")

        return cleaned_data

    def save(self):
        data = self.cleaned_data
        if self.matricula is None:
            return create_matricula(
                id_recibo=data["id_recibo"].pk,
                estado_matricula=data["estado_matricula"],
            )
        return update_matricula(
            id_matricula=self.matricula.id_matricula,
            id_facultad=self.matricula.id_facultad,
            id_recibo=data["id_recibo"].pk,
            estado_matricula=data["estado_matricula"],
        )


def deactivate_tarifa_from_instance(tarifa):
    return deactivate_tarifa(id_tarifa_matricula=tarifa.id_tarifa_matricula)


def anular_recibo_from_instance(recibo):
    return anular_recibo(id_recibo=recibo.id_recibo)


def cancel_matricula_from_instance(matricula):
    return cancel_matricula(
        id_matricula=matricula.id_matricula,
        id_facultad=matricula.id_facultad,
    )
