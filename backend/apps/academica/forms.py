
from django import forms
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Count, Max

from apps.academica.distributed_write import (
    create_estudiante,
    create_grupo,
    create_inscripcion,
    update_estudiante,
    update_grupo,
    update_inscripcion,
)
from apps.academica.models import Inscripcion
from apps.accounts.roles import get_user_roles
from apps.accounts.scope import (
    get_coordinated_program_ids,
    is_superadmin,
)
from apps.estructura.models import Facultad, PeriodoAcademico, ProgramaAcademico
from apps.financiera.models import Matricula
from apps.reportes.models import (
    EstudianteDetalle,
    GrupoDetalle,
    InscripcionDetalle,
    UsuarioGlobal,
)

ACTIVE_GROUP_STATES = ("Abierto", "En curso")
ACTIVE_ENROLLMENT_STATES = ("Cursando", "Aprobada", "Reprobada")
WRITE_ROLES = {"estudiante", "coordinador", "decano", "superadmin"}
STUDENT_STATUS_CHOICES = (
    ("Activo", "Activo"),
    ("Inactivo", "Inactivo"),
    ("Suspendido", "Suspendido"),
    ("Retirado", "Retirado"),
    ("Egresado", "Egresado"),
)
GROUP_STATUS_CHOICES = (
    ("Abierto", "Abierto"),
    ("En curso", "En curso"),
    ("Finalizado", "Finalizado"),
    ("Cancelado", "Cancelado"),
)
ENROLLMENT_STATUS_CHOICES = (
    ("Cursando", "Cursando"),
    ("Aprobada", "Aprobada"),
    ("Reprobada", "Reprobada"),
    ("Cancelada", "Cancelada"),
)


def user_can_write_enrollments(user):
    roles = set(get_user_roles(user))
    return is_superadmin(user) or bool(roles.intersection(WRITE_ROLES))


def user_can_create_students(user):
    roles = set(get_user_roles(user))
    return is_superadmin(user) or "coordinador" in roles


def user_can_create_groups(user):
    roles = set(get_user_roles(user))
    return is_superadmin(user) or "coordinador" in roles


def _choice_rows(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        return cursor.fetchall()


def _candidate_user_ids():
    rows = _choice_rows(
        """
        select u.id_usuario
        from reportes.vw_usuarios_global u
        where u.is_active = true
          and not exists (
              select 1
              from reportes.vw_estudiantes_detalle e
              where e.id_usuario = u.id_usuario
          )
          and not exists (
              select 1
              from reportes.vw_profesores_detalle p
              where p.id_usuario = u.id_usuario
          )
          and not exists (
              select 1
              from public.usuario_groups ug
              join public.auth_group g on g.id = ug.group_id
              where ug.customuser_id = u.id_usuario
                and g.name in ('docente', 'administrativo', 'decano')
          )
          and lower(u.correo) not like %s
          and lower(u.nombre) not like %s
          and lower(u.correo) not like %s
        order by u.nombre, u.correo
        """,
        ["admin.%", "administrativo%", "%docente%"],
    )
    return [row[0] for row in rows]


def _selected_value(data, field):
    if not data:
        return None
    return data.get(field) or None


class EstudianteCreateForm(forms.Form):
    id_usuario = forms.ModelChoiceField(
        label="Usuario",
        queryset=UsuarioGlobal.objects.none(),
    )
    id_facultad = forms.ModelChoiceField(
        label="Facultad",
        queryset=Facultad.objects.none(),
        to_field_name="id_facultad",
    )
    id_programa_academico = forms.ModelChoiceField(
        label="Programa academico",
        queryset=ProgramaAcademico.objects.none(),
        to_field_name="id_programa_academico",
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

    def __init__(self, *args, user, estudiante=None, selected_facultad=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.estudiante = estudiante
        selected_facultad = _selected_value(self.data, "id_facultad") or (
            selected_facultad
        )

        faculty_queryset = Facultad.objects.all()
        program_queryset = ProgramaAcademico.objects.select_related("facultad").filter(
            estado="Activo",
        )
        if selected_facultad:
            program_queryset = program_queryset.filter(facultad_id=selected_facultad)
        if not is_superadmin(user):
            coordinated_program_ids = get_coordinated_program_ids(user)
            program_queryset = program_queryset.filter(
                id_programa_academico__in=coordinated_program_ids,
            )
            faculty_queryset = faculty_queryset.filter(
                programas__id_programa_academico__in=coordinated_program_ids,
            )

        self.fields["id_facultad"].queryset = faculty_queryset.distinct().order_by(
            "nombre_facultad",
        )
        if selected_facultad:
            self.fields["id_facultad"].initial = selected_facultad
        self.fields["id_programa_academico"].queryset = program_queryset.order_by(
            "nombre_programa",
        )
        candidate_ids = _candidate_user_ids()
        user_queryset = UsuarioGlobal.objects.filter(id_usuario__in=candidate_ids)
        if estudiante is not None and estudiante.id_usuario:
            user_queryset = user_queryset | UsuarioGlobal.objects.filter(
                id_usuario=estudiante.id_usuario,
            )
        self.fields["id_usuario"].queryset = user_queryset.order_by("nombre", "correo")
        self.fields["id_usuario"].label_from_instance = (
            lambda user: f"{user.nombre} <{user.correo}>"
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        if estudiante is not None:
            self.fields["id_facultad"].disabled = True
            self.fields["id_usuario"].disabled = True
            self.fields["id_usuario"].initial = estudiante.id_usuario
            self.fields["id_facultad"].initial = estudiante.id_facultad
            self.fields["id_programa_academico"].initial = (
                estudiante.id_programa_academico
            )
            self.fields["limite_matriculas"].initial = estudiante.limite_matriculas
            self.fields["estado_estudiante"].initial = estudiante.estado_estudiante

    def clean(self):
        cleaned_data = super().clean()
        id_usuario = cleaned_data.get("id_usuario")
        faculty = cleaned_data.get("id_facultad")
        program = cleaned_data.get("id_programa_academico")
        limite_matriculas = cleaned_data.get("limite_matriculas")

        if not user_can_create_students(self.user):
            raise ValidationError("No tienes permisos para gestionar estudiantes.")

        if not faculty:
            raise ValidationError("La facultad es obligatoria.")

        if limite_matriculas is not None and limite_matriculas <= 0:
            raise ValidationError("El limite de matriculas debe ser mayor que cero.")

        if program and program not in self.fields["id_programa_academico"].queryset:
            raise ValidationError("El programa seleccionado esta fuera de tu alcance.")

        if program and faculty and program.facultad_id != faculty.id_facultad:
            raise ValidationError(
                "El programa seleccionado no pertenece a la facultad.",
            )

        if id_usuario:
            existing_students = EstudianteDetalle.objects.filter(
                id_usuario=id_usuario.pk,
            )
            if self.estudiante is not None:
                existing_students = existing_students.exclude(
                    id_estudiante=self.estudiante.id_estudiante,
                )
            if existing_students.exists():
                raise ValidationError("El usuario seleccionado ya tiene estudiante.")

        return cleaned_data

    def save(self):
        return create_estudiante(
            id_usuario=self.cleaned_data["id_usuario"].pk,
            id_facultad=self.cleaned_data["id_facultad"].pk,
            id_programa_academico=self.cleaned_data["id_programa_academico"].pk,
            limite_matriculas=self.cleaned_data["limite_matriculas"],
            estado_estudiante=self.cleaned_data["estado_estudiante"],
        )


class EstudianteUpdateForm(EstudianteCreateForm):
    def save(self):
        return update_estudiante(
            id_estudiante=self.estudiante.id_estudiante,
            id_usuario=self.cleaned_data["id_usuario"].pk,
            id_facultad=self.cleaned_data["id_facultad"].pk,
            id_programa_academico=self.cleaned_data["id_programa_academico"].pk,
            limite_matriculas=self.cleaned_data["limite_matriculas"],
            estado_estudiante=self.cleaned_data["estado_estudiante"],
        )


class GrupoCreateForm(forms.Form):
    id_facultad = forms.ModelChoiceField(
        label="Facultad",
        queryset=Facultad.objects.none(),
        to_field_name="id_facultad",
    )
    id_programa_asignatura = forms.ChoiceField(label="Asignatura del programa")
    id_periodo_academico = forms.ModelChoiceField(
        label="Periodo academico",
        queryset=PeriodoAcademico.objects.none(),
        to_field_name="id_periodo_academico",
    )
    id_profesor = forms.ChoiceField(label="Docente", required=False)
    codigo_grupo = forms.CharField(label="Codigo de grupo", max_length=20)
    cupo_maximo = forms.IntegerField(label="Cupo maximo", min_value=1, initial=30)
    estado_grupo = forms.ChoiceField(
        label="Estado",
        choices=GROUP_STATUS_CHOICES,
        initial="Abierto",
    )

    def __init__(self, *args, user, grupo=None, selected_facultad=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.grupo = grupo
        selected_facultad = _selected_value(self.data, "id_facultad") or (
            selected_facultad
        )

        faculty_queryset = Facultad.objects.all()
        program_ids = None
        if not is_superadmin(user):
            program_ids = get_coordinated_program_ids(user)
            faculty_queryset = faculty_queryset.filter(
                programas__id_programa_academico__in=program_ids,
            )

        self.fields["id_facultad"].queryset = faculty_queryset.distinct().order_by(
            "nombre_facultad",
        )
        if selected_facultad:
            self.fields["id_facultad"].initial = selected_facultad
        self.fields["id_periodo_academico"].queryset = (
            PeriodoAcademico.objects.order_by(
                "-fecha_inicio",
                "id_periodo_academico",
            )
        )
        self.fields["id_programa_asignatura"].choices = (
            self._programa_asignatura_choices(program_ids, selected_facultad)
        )
        self.fields["id_profesor"].choices = self._profesor_choices(selected_facultad)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        if grupo is not None:
            self.fields["id_facultad"].disabled = True
            self.fields["id_facultad"].initial = grupo.id_facultad
            self.fields["id_programa_asignatura"].initial = str(
                grupo.id_programa_asignatura,
            )
            self.fields["id_periodo_academico"].initial = grupo.id_periodo_academico
            self.fields["id_profesor"].initial = str(grupo.id_profesor or "")
            self.fields["codigo_grupo"].initial = grupo.codigo_grupo
            self.fields["cupo_maximo"].initial = grupo.cupo_maximo
            self.fields["estado_grupo"].initial = grupo.estado_grupo

    def _programa_asignatura_choices(self, program_ids, selected_facultad=None):
        where = ["pa.estado = 'Activa'"]
        params = []
        if selected_facultad:
            where.append("pa.id_facultad = %s")
            params.append(selected_facultad)
        if program_ids is not None:
            if not program_ids:
                return [("", "Seleccione una asignatura")]
            where.append("pa.id_programa_academico = any(%s)")
            params.append(program_ids)
        rows = _choice_rows(
            f"""
            select
                pa.id_programa_asignatura::text,
                pa.id_facultad,
                pa.id_programa_academico,
                coalesce(a.nombre_asignatura, pa.cod_asignatura) as asignatura
            from reportes.vw_programa_asignatura_global pa
            left join institucional.asignatura a
              on a.cod_asignatura = pa.cod_asignatura
            where {" and ".join(where)}
            order by pa.id_facultad, pa.id_programa_academico, asignatura
            """,
            params,
        )
        return [
            ("", "Seleccione una asignatura"),
            *[
                (
                    row[0],
                    f"{row[1]} - {row[2]} - {row[3]}",
                )
                for row in rows
            ],
        ]

    def _profesor_choices(self, selected_facultad=None):
        where = []
        params = []
        if selected_facultad:
            where.append("id_facultad = %s")
            params.append(selected_facultad)
        where_sql = f"where {' and '.join(where)}" if where else ""
        rows = _choice_rows(
            f"""
            select id_profesor::text, id_facultad, coalesce(profesor, correo)
            from reportes.vw_profesores_detalle
            {where_sql}
            order by id_facultad, profesor
            """,
            params,
        )
        return [
            ("", "Sin asignar"),
            *[(row[0], f"{row[1]} - {row[2]}") for row in rows],
        ]

    def clean(self):
        cleaned_data = super().clean()
        faculty = cleaned_data.get("id_facultad")
        id_programa_asignatura = cleaned_data.get("id_programa_asignatura")
        id_profesor = cleaned_data.get("id_profesor")
        codigo_grupo = cleaned_data.get("codigo_grupo")
        cupo_maximo = cleaned_data.get("cupo_maximo")

        if not user_can_create_groups(self.user):
            raise ValidationError("No tienes permisos para gestionar grupos.")

        if not faculty:
            raise ValidationError("La facultad es obligatoria.")

        if not codigo_grupo:
            raise ValidationError("El codigo de grupo es obligatorio.")

        if cupo_maximo is not None and cupo_maximo <= 0:
            raise ValidationError("El cupo maximo debe ser mayor que cero.")

        if faculty and id_programa_asignatura:
            rows = _choice_rows(
                """
                select id_facultad
                from reportes.vw_programa_asignatura_global
                where id_programa_asignatura = %s
                """,
                [id_programa_asignatura],
            )
            if not rows:
                raise ValidationError("La asignatura del programa no existe.")
            if rows[0][0] != faculty.id_facultad:
                raise ValidationError(
                    "La asignatura del programa no pertenece a la facultad.",
                )

        if faculty and id_profesor:
            rows = _choice_rows(
                """
                select id_facultad
                from reportes.vw_profesores_detalle
                where id_profesor = %s
                """,
                [id_profesor],
            )
            if not rows:
                raise ValidationError("El docente seleccionado no existe.")
            if rows[0][0] != faculty.id_facultad:
                raise ValidationError("El docente no pertenece a la facultad.")

        return cleaned_data

    def save(self):
        return create_grupo(
            id_facultad=self.cleaned_data["id_facultad"].pk,
            id_programa_asignatura=self.cleaned_data["id_programa_asignatura"],
            id_periodo_academico=self.cleaned_data["id_periodo_academico"].pk,
            id_profesor=self.cleaned_data.get("id_profesor") or None,
            codigo_grupo=self.cleaned_data["codigo_grupo"],
            cupo_maximo=self.cleaned_data["cupo_maximo"],
            estado_grupo=self.cleaned_data["estado_grupo"],
        )


class GrupoUpdateForm(GrupoCreateForm):
    def save(self):
        return update_grupo(
            id_grupo=self.grupo.id_grupo,
            id_facultad=self.cleaned_data["id_facultad"].pk,
            id_programa_asignatura=self.cleaned_data["id_programa_asignatura"],
            id_periodo_academico=self.cleaned_data["id_periodo_academico"].pk,
            id_profesor=self.cleaned_data.get("id_profesor") or None,
            codigo_grupo=self.cleaned_data["codigo_grupo"],
            cupo_maximo=self.cleaned_data["cupo_maximo"],
            estado_grupo=self.cleaned_data["estado_grupo"],
        )


class InscripcionCreateForm(forms.Form):
    id_estudiante = forms.ModelChoiceField(
        label="Estudiante",
        queryset=EstudianteDetalle.objects.none(),
    )
    id_grupo = forms.ModelChoiceField(
        label="Grupo",
        queryset=GrupoDetalle.objects.none(),
    )
    intento = forms.IntegerField(label="Intento", min_value=1, initial=1)
    estado_inscripcion = forms.ChoiceField(
        label="Estado",
        choices=ENROLLMENT_STATUS_CHOICES,
        initial="Cursando",
    )
    nota1 = forms.DecimalField(
        label="Nota 1",
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=5,
        required=False,
    )
    nota2 = forms.DecimalField(
        label="Nota 2",
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=5,
        required=False,
    )
    nota3 = forms.DecimalField(
        label="Nota 3",
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=5,
        required=False,
    )
    nota_final = forms.DecimalField(
        label="Nota final",
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=5,
        required=False,
    )

    def __init__(
        self,
        *args,
        user,
        inscripcion=None,
        selected_facultad=None,
        selected_periodo=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.user = user
        self.inscripcion = inscripcion
        selected_facultad = _selected_value(self.data, "id_facultad") or (
            selected_facultad
        )
        selected_periodo = _selected_value(self.data, "id_periodo_academico") or (
            selected_periodo
        )

        student_queryset = EstudianteDetalle.objects.order_by(
            "nombre_facultad", "nombre_programa", "estudiante"
        )
        group_queryset = GrupoDetalle.objects.exclude(
            estado_grupo="Cancelado",
        )
        if selected_facultad:
            student_queryset = student_queryset.filter(id_facultad=selected_facultad)
            group_queryset = group_queryset.filter(id_facultad=selected_facultad)
        if selected_periodo:
            group_queryset = group_queryset.filter(
                id_periodo_academico=selected_periodo,
            )
        self.fields["id_estudiante"].queryset = student_queryset
        self.fields["id_grupo"].queryset = group_queryset.order_by(
            "nombre_facultad",
            "id_periodo_academico",
            "nombre_asignatura",
            "codigo_grupo",
        )
        self.fields["id_estudiante"].label_from_instance = (
            lambda student: (
                f"{student.nombre_facultad} - {student.estudiante} "
                f"({student.nombre_programa}) - {student.correo}"
            )
        )
        self.fields["id_grupo"].label_from_instance = (
            lambda group: (
                f"{group.nombre_facultad} - {group.id_periodo_academico} - "
                f"{group.nombre_programa} - {group.nombre_asignatura} - "
                f"Grupo {group.codigo_grupo}"
            )
        )

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        if inscripcion is not None:
            self.fields["id_estudiante"].disabled = True
            self.fields["id_grupo"].disabled = True
            self.fields["id_estudiante"].initial = inscripcion.id_estudiante
            self.fields["id_grupo"].initial = inscripcion.id_grupo
            self.fields["intento"].initial = inscripcion.intento
            self.fields["estado_inscripcion"].initial = inscripcion.estado_inscripcion
            self.fields["nota1"].initial = getattr(inscripcion, "nota1", None)
            self.fields["nota2"].initial = getattr(inscripcion, "nota2", None)
            self.fields["nota3"].initial = getattr(inscripcion, "nota3", None)
            self.fields["nota_final"].initial = inscripcion.nota_final

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("id_estudiante")
        group = cleaned_data.get("id_grupo")
        estado = cleaned_data.get("estado_inscripcion")
        nota_final = cleaned_data.get("nota_final")
        intento = cleaned_data.get("intento")

        if not user_can_write_enrollments(self.user):
            raise ValidationError("No tienes permisos para gestionar inscripciones.")

        if intento is not None and intento <= 0:
            raise ValidationError("El intento debe ser mayor que cero.")

        if estado in {"Aprobada", "Reprobada"} and nota_final is None:
            raise ValidationError(
                "La nota final es obligatoria para aprobar o reprobar.",
            )

        if not student or not group:
            return cleaned_data

        if student.id_facultad != group.id_facultad:
            raise ValidationError(
                "El estudiante y el grupo deben estar en la facultad.",
            )

        duplicate = InscripcionDetalle.objects.filter(
            id_estudiante=student.id_estudiante,
            id_grupo=group.id_grupo,
        )
        if self.inscripcion is not None:
            duplicate = duplicate.exclude(
                id_inscripcion=self.inscripcion.id_inscripcion,
            )
        if duplicate.exists():
            raise ValidationError("El estudiante ya esta inscrito en este grupo.")

        return cleaned_data

    def save(self):
        return create_inscripcion(
            id_estudiante=self.cleaned_data["id_estudiante"].pk,
            id_grupo=self.cleaned_data["id_grupo"].pk,
            nota1=self.cleaned_data.get("nota1"),
            nota2=self.cleaned_data.get("nota2"),
            nota3=self.cleaned_data.get("nota3"),
            nota_final=self.cleaned_data.get("nota_final"),
            intento=self.cleaned_data["intento"],
            estado_inscripcion=self.cleaned_data["estado_inscripcion"],
        )


class InscripcionUpdateForm(InscripcionCreateForm):
    def save(self):
        return update_inscripcion(
            id_inscripcion=self.inscripcion.id_inscripcion,
            id_facultad=self.inscripcion.id_facultad,
            id_estudiante=self.cleaned_data["id_estudiante"].pk,
            id_grupo=self.cleaned_data["id_grupo"].pk,
            nota1=self.cleaned_data.get("nota1"),
            nota2=self.cleaned_data.get("nota2"),
            nota3=self.cleaned_data.get("nota3"),
            nota_final=self.cleaned_data.get("nota_final"),
            intento=self.cleaned_data["intento"],
            estado_inscripcion=self.cleaned_data["estado_inscripcion"],
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
