import uuid
from decimal import Decimal

from django import forms
from django.utils import timezone

from apps.academica.models import Grupo, Profesor, ProgramaAsignatura
from apps.accounts.roles import get_user_roles
from apps.accounts.scope import (
    get_coordinated_program_ids,
    get_professor_for_user,
    get_student_for_user,
    is_superadmin,
)
from apps.homologaciones.models import Homologacion


def _professors_for_program(program_id):
    professors_from_groups = Profesor.objects.filter(
        grupos__programa_asignatura__programa_academico_id=program_id,
    )
    professors_from_faculty = Profesor.objects.filter(
        facultad__programas__id_programa_academico=program_id,
    )
    return (
        (professors_from_groups | professors_from_faculty)
        .select_related(
            "usuario",
            "facultad",
        )
        .distinct()
    )


def _default_evaluator_for_program_assignment(program_assignment):
    professor = (
        Grupo.objects.filter(
            programa_asignatura=program_assignment,
            profesor__isnull=False,
        )
        .select_related("profesor__usuario", "profesor__facultad")
        .order_by("profesor__usuario__nombre")
        .first()
    )
    if professor:
        return professor.profesor

    return _professors_for_program(
        program_assignment.programa_academico_id,
    ).first()


class HomologacionSolicitudForm(forms.ModelForm):
    class Meta:
        model = Homologacion
        fields = [
            "asignatura_origen",
            "institucion_origen",
            "programa_asignatura",
            "observacion",
        ]
        labels = {
            "asignatura_origen": "Asignatura de origen",
            "institucion_origen": "Institucion de origen",
            "programa_asignatura": "Asignatura a homologar",
            "observacion": "Observacion",
        }
        widgets = {
            "observacion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.student = get_student_for_user(user)
        self.evaluator = None
        queryset = ProgramaAsignatura.objects.none()
        if self.student:
            queryset = ProgramaAsignatura.objects.select_related(
                "asignatura",
                "programa_academico",
            ).filter(
                programa_academico=self.student.programa_academico,
                asignatura__homologable=True,
                estado="Activa",
            )
        self.fields["programa_asignatura"].queryset = queryset
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned_data = super().clean()
        program_assignment = cleaned_data.get("programa_asignatura")

        if not self.student:
            raise forms.ValidationError(
                "El usuario autenticado no tiene un registro de estudiante asociado.",
            )

        if not program_assignment:
            return cleaned_data

        if (
            program_assignment.programa_academico_id
            != self.student.programa_academico_id
        ):
            raise forms.ValidationError(
                "La asignatura destino debe pertenecer al programa del estudiante.",
            )

        if not program_assignment.asignatura.homologable:
            raise forms.ValidationError(
                "La asignatura seleccionada no esta marcada como homologable.",
            )

        if Homologacion.objects.filter(
            estudiante=self.student,
            programa_asignatura=program_assignment,
            estado_homologacion=Homologacion.EstadoHomologacion.APROBADA,
        ).exists():
            raise forms.ValidationError(
                "Ya existe una homologacion aprobada para esta asignatura.",
            )

        self.evaluator = _default_evaluator_for_program_assignment(program_assignment)
        if not self.evaluator:
            raise forms.ValidationError(
                "No hay un profesor disponible para recibir la solicitud.",
            )

        return cleaned_data

    def save(self, commit=True):
        homologacion = super().save(commit=False)
        homologacion.id_homologacion = uuid.uuid4()
        homologacion.estudiante = self.student
        homologacion.profesor_evaluador = self.evaluator
        homologacion.fecha_solicitud = timezone.localdate()
        homologacion.estado_homologacion = Homologacion.EstadoHomologacion.SOLICITADA
        homologacion.fecha_respuesta = None
        homologacion.nota_obtenida = None
        if commit:
            homologacion.save()
        return homologacion


class HomologacionAsignarEvaluadorForm(forms.ModelForm):
    class Meta:
        model = Homologacion
        fields = ["profesor_evaluador"]
        labels = {"profesor_evaluador": "Profesor evaluador"}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        queryset = Profesor.objects.none()
        if is_superadmin(user):
            queryset = Profesor.objects.select_related("usuario", "facultad")
        else:
            program_ids = get_coordinated_program_ids(user)
            if program_ids:
                queryset = Profesor.objects.filter(
                    facultad__programas__id_programa_academico__in=program_ids,
                ).select_related("usuario", "facultad")
        self.fields["profesor_evaluador"].queryset = queryset.distinct()
        self.fields["profesor_evaluador"].widget.attrs.setdefault(
            "class",
            "form-control",
        )

    def clean(self):
        cleaned_data = super().clean()
        homologacion = self.instance

        if homologacion.estado_homologacion in {
            Homologacion.EstadoHomologacion.APROBADA,
            Homologacion.EstadoHomologacion.RECHAZADA,
            Homologacion.EstadoHomologacion.CANCELADA,
        }:
            raise forms.ValidationError(
                "Solo se puede asignar evaluador a solicitudes abiertas.",
            )

        return cleaned_data

    def save(self, commit=True):
        homologacion = super().save(commit=False)
        homologacion.estado_homologacion = Homologacion.EstadoHomologacion.EN_REVISION
        if commit:
            homologacion.save()
        return homologacion


class HomologacionEvaluarForm(forms.ModelForm):
    accion = forms.ChoiceField(
        choices=(
            (Homologacion.EstadoHomologacion.APROBADA, "Aprobar"),
            (Homologacion.EstadoHomologacion.RECHAZADA, "Rechazar"),
        ),
        label="Decision",
    )

    class Meta:
        model = Homologacion
        fields = ["accion", "nota_obtenida", "observacion"]
        labels = {
            "nota_obtenida": "Nota obtenida",
            "observacion": "Observacion",
        }
        widgets = {
            "observacion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("accion")
        grade = cleaned_data.get("nota_obtenida")
        observation = cleaned_data.get("observacion")
        homologacion = self.instance

        if (
            homologacion.estado_homologacion
            == Homologacion.EstadoHomologacion.CANCELADA
        ):
            raise forms.ValidationError("No se puede evaluar una solicitud cancelada.")
        if homologacion.estado_homologacion not in {
            Homologacion.EstadoHomologacion.SOLICITADA,
            Homologacion.EstadoHomologacion.EN_REVISION,
        }:
            raise forms.ValidationError(
                "Solo se pueden evaluar solicitudes abiertas o en revision.",
            )

        roles = set(get_user_roles(self.user))
        professor = get_professor_for_user(self.user)
        if not is_superadmin(self.user) and (
            "docente" not in roles or professor != homologacion.profesor_evaluador
        ):
            raise forms.ValidationError(
                "Solo el docente evaluador asignado puede evaluar esta solicitud.",
            )

        if action == Homologacion.EstadoHomologacion.APROBADA:
            if grade is None:
                raise forms.ValidationError(
                    "Una homologacion aprobada debe tener nota obtenida.",
                )
            if grade < Decimal("0.0") or grade > Decimal("5.0"):
                raise forms.ValidationError("La nota debe estar entre 0.0 y 5.0.")
            if (
                Homologacion.objects.filter(
                    estudiante=homologacion.estudiante,
                    programa_asignatura=homologacion.programa_asignatura,
                    estado_homologacion=Homologacion.EstadoHomologacion.APROBADA,
                )
                .exclude(pk=homologacion.pk)
                .exists()
            ):
                raise forms.ValidationError(
                    "Ya existe una homologacion aprobada para esta asignatura.",
                )

        if action == Homologacion.EstadoHomologacion.RECHAZADA and not observation:
            raise forms.ValidationError(
                "La observacion es obligatoria al rechazar una solicitud.",
            )

        return cleaned_data

    def save(self, commit=True):
        homologacion = super().save(commit=False)
        homologacion.estado_homologacion = self.cleaned_data["accion"]
        homologacion.fecha_respuesta = timezone.localdate()
        if (
            homologacion.estado_homologacion
            == Homologacion.EstadoHomologacion.RECHAZADA
        ):
            homologacion.nota_obtenida = None
        if commit:
            homologacion.save()
        return homologacion
