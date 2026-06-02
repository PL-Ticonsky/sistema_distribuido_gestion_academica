import uuid

from django import forms
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Max

from apps.academica.models import Estudiante, Grupo, Inscripcion
from apps.accounts.models import CustomUser
from apps.accounts.roles import get_user_roles
from apps.accounts.scope import (
    get_coordinated_program_ids,
    get_student_for_user,
    get_visible_group_ids,
    get_visible_student_ids,
    is_superadmin,
)
from apps.estructura.models import ProgramaAcademico
from apps.financiera.models import Matricula

ACTIVE_GROUP_STATES = ("Abierto", "En curso")
ACTIVE_ENROLLMENT_STATES = ("Cursando", "Aprobada", "Reprobada")
WRITE_ROLES = {"estudiante", "coordinador", "decano", "superadmin"}
DEMO_STUDENT_PASSWORD = "Demo12345*"
STUDENT_STATUS_CHOICES = (
    ("Activo", "Activo"),
    ("Inactivo", "Inactivo"),
    ("Suspendido", "Suspendido"),
    ("Retirado", "Retirado"),
    ("Egresado", "Egresado"),
)


def user_can_write_enrollments(user):
    roles = set(get_user_roles(user))
    return is_superadmin(user) or bool(roles.intersection(WRITE_ROLES))


def user_can_create_students(user):
    roles = set(get_user_roles(user))
    return is_superadmin(user) or "coordinador" in roles


class EstudianteCreateForm(forms.Form):
    nombre = forms.CharField(label="Nombre completo", max_length=80)
    correo = forms.EmailField(label="Correo institucional", max_length=254)
    tipo_de_documento = forms.ChoiceField(
        label="Tipo de documento",
        choices=CustomUser.TipoDocumento.choices,
    )
    numero_de_documento = forms.CharField(label="Numero de documento", max_length=20)
    direccion = forms.CharField(label="Direccion", max_length=120, required=False)
    programa_academico = forms.ModelChoiceField(
        label="Programa academico",
        queryset=ProgramaAcademico.objects.none(),
    )
    limite_matriculas = forms.IntegerField(
        label="Limite de matriculas",
        min_value=1,
        initial=15,
    )
    estado_estudiante = forms.ChoiceField(
        label="Estado del estudiante",
        choices=STUDENT_STATUS_CHOICES,
        initial="Activo",
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        program_queryset = ProgramaAcademico.objects.select_related("facultad").filter(
            estado="Activo",
        )
        if not is_superadmin(user):
            program_queryset = program_queryset.filter(
                id_programa_academico__in=get_coordinated_program_ids(user),
            )
        self.fields["programa_academico"].queryset = program_queryset.order_by(
            "nombre_programa",
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_correo(self):
        correo = CustomUser.objects.normalize_email(self.cleaned_data["correo"])
        if CustomUser.objects.filter(correo__iexact=correo).exists():
            raise ValidationError("Ya existe un usuario registrado con este correo.")
        return correo

    def clean(self):
        cleaned_data = super().clean()
        tipo_de_documento = cleaned_data.get("tipo_de_documento")
        numero_de_documento = cleaned_data.get("numero_de_documento")
        program = cleaned_data.get("programa_academico")

        if not user_can_create_students(self.user):
            raise ValidationError("No tienes permisos para agregar estudiantes.")

        if tipo_de_documento and numero_de_documento:
            if CustomUser.objects.filter(
                tipo_de_documento=tipo_de_documento,
                numero_de_documento=numero_de_documento,
            ).exists():
                raise ValidationError(
                    "Ya existe un usuario con este tipo y numero de documento.",
                )

        if program and program not in self.fields["programa_academico"].queryset:
            raise ValidationError("El programa seleccionado esta fuera de tu alcance.")

        return cleaned_data

    @transaction.atomic
    def save(self):
        user = CustomUser.objects.create_user(
            correo=self.cleaned_data["correo"],
            password=DEMO_STUDENT_PASSWORD,
            nombre=self.cleaned_data["nombre"],
            tipo_de_documento=self.cleaned_data["tipo_de_documento"],
            numero_de_documento=self.cleaned_data["numero_de_documento"],
            direccion=self.cleaned_data.get("direccion") or None,
            is_active=True,
        )
        student_group, _ = Group.objects.get_or_create(name="estudiante")
        user.groups.add(student_group)

        return Estudiante.objects.create(
            id_estudiante=uuid.uuid4(),
            usuario=user,
            programa_academico=self.cleaned_data["programa_academico"],
            limite_matriculas=self.cleaned_data["limite_matriculas"],
            estado_estudiante=self.cleaned_data["estado_estudiante"],
        )


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
