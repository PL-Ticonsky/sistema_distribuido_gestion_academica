import uuid

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Count, Max

from apps.academica.models import Estudiante, Grupo, Inscripcion
from apps.accounts.roles import get_user_roles
from apps.accounts.scope import (
    get_student_for_user,
    get_visible_group_ids,
    get_visible_student_ids,
    is_superadmin,
)
from apps.financiera.models import Matricula

ACTIVE_GROUP_STATES = ("Abierto", "En curso")
ACTIVE_ENROLLMENT_STATES = ("Cursando", "Aprobada", "Reprobada")
WRITE_ROLES = {"estudiante", "coordinador", "decano", "superadmin"}


def user_can_write_enrollments(user):
    roles = set(get_user_roles(user))
    return is_superadmin(user) or bool(roles.intersection(WRITE_ROLES))


class InscripcionCreateForm(forms.Form):
    estudiante = forms.ModelChoiceField(
        queryset=Estudiante.objects.none(),
        required=False,
        label="Estudiante",
    )
    grupo = forms.ModelChoiceField(
        queryset=Grupo.objects.none(),
        label="Grupo",
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.roles = set(get_user_roles(user))
        self.student = get_student_for_user(user)

        if is_superadmin(user):
            student_queryset = Estudiante.objects.select_related(
                "usuario",
                "programa_academico",
            )
            group_queryset = Grupo.objects.select_related(
                "programa_asignatura__asignatura",
                "programa_asignatura__programa_academico",
                "periodo_academico",
            )
        else:
            student_ids = get_visible_student_ids(user)
            group_ids = get_visible_group_ids(user)
            student_queryset = Estudiante.objects.select_related(
                "usuario",
                "programa_academico",
            ).filter(id_estudiante__in=student_ids)
            group_queryset = Grupo.objects.select_related(
                "programa_asignatura__asignatura",
                "programa_asignatura__programa_academico",
                "periodo_academico",
            ).filter(id_grupo__in=group_ids)

        if self._is_student_only():
            self.fields["estudiante"].required = False
            self.fields["estudiante"].widget = forms.HiddenInput()
            if self.student:
                self.fields["estudiante"].queryset = Estudiante.objects.filter(
                    pk=self.student.pk,
                )
                group_queryset = Grupo.objects.select_related(
                    "programa_asignatura__asignatura",
                    "programa_asignatura__programa_academico",
                    "periodo_academico",
                ).filter(
                    programa_asignatura__programa_academico=self.student.programa_academico,
                )
            else:
                self.fields["estudiante"].queryset = Estudiante.objects.none()
                group_queryset = Grupo.objects.none()
        else:
            self.fields["estudiante"].required = True
            self.fields["estudiante"].queryset = student_queryset.order_by(
                "usuario__nombre",
            )

        self.fields["grupo"].queryset = group_queryset.filter(
            estado_grupo__in=ACTIVE_GROUP_STATES,
        ).order_by(
            "periodo_academico__id_periodo_academico",
            "programa_asignatura__asignatura__nombre_asignatura",
            "codigo_grupo",
        )

    def _is_student_only(self):
        elevated_roles = {"coordinador", "decano", "superadmin"}
        return "estudiante" in self.roles and not self.roles.intersection(
            elevated_roles
        )

    def clean(self):
        cleaned_data = super().clean()

        if not user_can_write_enrollments(self.user):
            raise ValidationError("No tienes permisos para crear inscripciones.")

        estudiante = cleaned_data.get("estudiante")
        grupo = cleaned_data.get("grupo")

        if self._is_student_only():
            estudiante = self.student
            cleaned_data["estudiante"] = estudiante
            if not estudiante:
                raise ValidationError(
                    "Tu usuario no tiene un registro de estudiante asociado.",
                )

        if not estudiante or not grupo:
            return cleaned_data

        validate_enrollment_business_rules(estudiante, grupo)
        cleaned_data["intento"] = calculate_attempt(estudiante, grupo)
        return cleaned_data

    def save(self):
        return Inscripcion.objects.create(
            id_inscripcion=uuid.uuid4(),
            estudiante=self.cleaned_data["estudiante"],
            grupo=self.cleaned_data["grupo"],
            intento=self.cleaned_data["intento"],
            estado_inscripcion="Cursando",
        )


def validate_enrollment_business_rules(estudiante, grupo):
    if grupo.estado_grupo not in ACTIVE_GROUP_STATES:
        raise ValidationError("El grupo no esta abierto para inscripciones.")

    if Inscripcion.objects.filter(estudiante=estudiante, grupo=grupo).exists():
        raise ValidationError("El estudiante ya esta inscrito en este grupo.")

    same_subject_same_period_exists = Inscripcion.objects.filter(
        estudiante=estudiante,
        grupo__periodo_academico=grupo.periodo_academico,
        grupo__programa_asignatura__asignatura=grupo.programa_asignatura.asignatura,
    ).exclude(estado_inscripcion="Cancelada")
    if same_subject_same_period_exists.exists():
        raise ValidationError(
            "El estudiante ya tiene una inscripcion para esta asignatura "
            "en el periodo.",
        )

    enrolled_count = (
        Inscripcion.objects.filter(
            grupo=grupo,
        )
        .exclude(estado_inscripcion="Cancelada")
        .count()
    )
    if enrolled_count >= grupo.cupo_maximo:
        raise ValidationError("El grupo no tiene cupos disponibles.")

    has_active_enrollment = Matricula.objects.filter(
        recibo__estudiante=estudiante,
        recibo__tarifa_matricula__periodo_academico=grupo.periodo_academico,
        estado_matricula="Activa",
    ).exists()
    if not has_active_enrollment:
        raise ValidationError(
            "El estudiante no tiene matricula activa para el periodo del grupo.",
        )


def calculate_attempt(estudiante, grupo):
    previous_attempt = (
        Inscripcion.objects.filter(
            estudiante=estudiante,
            grupo__programa_asignatura__asignatura=grupo.programa_asignatura.asignatura,
        )
        .aggregate(max_attempt=Max("intento"))
        .get("max_attempt")
    )
    return (previous_attempt or 0) + 1


def get_enrollment_counts_by_group(group_ids):
    if not group_ids:
        return {}

    rows = (
        Inscripcion.objects.filter(grupo_id__in=group_ids)
        .exclude(estado_inscripcion="Cancelada")
        .values("grupo_id")
        .annotate(total=Count("id_inscripcion"))
    )
    return {row["grupo_id"]: row["total"] for row in rows}


class NotaInscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ("nota1", "nota2", "nota3")

    def clean(self):
        cleaned_data = super().clean()

        if self.instance.estado_inscripcion == "Cancelada":
            raise ValidationError(
                "No se pueden modificar notas de inscripciones canceladas."
            )

        for field_name in ("nota1", "nota2", "nota3"):
            value = cleaned_data.get(field_name)
            if value is not None and not 0 <= value <= 5:
                raise ValidationError("Las notas deben estar entre 0.0 y 5.0.")

        return cleaned_data

    def save(self, commit=True):
        inscripcion = super().save(commit=False)
        notas = [inscripcion.nota1, inscripcion.nota2, inscripcion.nota3]

        if all(nota is not None for nota in notas):
            inscripcion.nota_final = sum(notas) / 3
            if inscripcion.nota_final >= 3:
                inscripcion.estado_inscripcion = "Aprobada"
            else:
                inscripcion.estado_inscripcion = "Reprobada"
        else:
            inscripcion.nota_final = None
            inscripcion.estado_inscripcion = "Cursando"

        if commit:
            inscripcion.save(
                update_fields=[
                    "nota1",
                    "nota2",
                    "nota3",
                    "nota_final",
                    "estado_inscripcion",
                ],
            )
        return inscripcion
