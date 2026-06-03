from django import forms
from django.core.exceptions import ValidationError
from django.db import connection
from django.utils import timezone

from apps.academica.distributed_write import (
    asignar_evaluador_homologacion,
    create_homologacion,
    evaluar_homologacion,
    update_homologacion,
)
from apps.reportes.models import EstudianteDetalle, ProfesorDetalle

HOMOLOGACION_STATUS_CHOICES = (
    ("Solicitada", "Solicitada"),
    ("En revision", "En revision"),
    ("Aprobada", "Aprobada"),
    ("Rechazada", "Rechazada"),
    ("Cancelada", "Cancelada"),
)

EVALUATION_STATUS_CHOICES = (
    ("Aprobada", "Aprobada"),
    ("Rechazada", "Rechazada"),
)


def _choice_rows(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        return cursor.fetchall()


def _data_value(data, field):
    if not data:
        return None
    return data.get(field) or None


def _facultad_for_student(id_estudiante):
    if not id_estudiante:
        return None
    rows = _choice_rows(
        """
        select id_facultad
        from reportes.vw_estudiantes_detalle
        where id_estudiante = %s
        """,
        [id_estudiante],
    )
    return rows[0][0] if rows else None


class HomologacionForm(forms.Form):
    id_estudiante = forms.ModelChoiceField(
        label="Estudiante",
        queryset=EstudianteDetalle.objects.none(),
    )
    id_profesor_evaluador = forms.ModelChoiceField(
        label="Profesor evaluador",
        queryset=ProfesorDetalle.objects.none(),
    )
    asignatura_origen = forms.CharField(label="Asignatura origen", max_length=120)
    institucion_origen = forms.CharField(label="Institucion origen", max_length=120)
    id_programa_asignatura = forms.ChoiceField(label="Asignatura destino")
    fecha_solicitud = forms.DateField(
        label="Fecha de solicitud",
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    estado_homologacion = forms.ChoiceField(
        label="Estado",
        choices=HOMOLOGACION_STATUS_CHOICES,
        initial="Solicitada",
    )

    def __init__(self, *args, homologacion=None, selected_facultad=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.homologacion = homologacion
        selected_student = _data_value(self.data, "id_estudiante")
        selected_facultad = (
            _facultad_for_student(selected_student)
            or selected_facultad
            or getattr(homologacion, "id_facultad", None)
        )
        student_queryset = EstudianteDetalle.objects.order_by(
            "nombre_facultad",
            "nombre_programa",
            "estudiante",
        )
        professor_queryset = ProfesorDetalle.objects.order_by(
            "nombre_facultad",
            "profesor",
        )
        if selected_facultad:
            student_queryset = student_queryset.filter(id_facultad=selected_facultad)
            professor_queryset = professor_queryset.filter(
                id_facultad=selected_facultad,
            )
        self.fields["id_estudiante"].queryset = student_queryset
        self.fields["id_profesor_evaluador"].queryset = professor_queryset
        self.fields["id_estudiante"].label_from_instance = (
            lambda student: (
                f"{student.nombre_facultad} - {student.estudiante} "
                f"({student.nombre_programa})"
            )
        )
        self.fields["id_profesor_evaluador"].label_from_instance = (
            lambda professor: (
                f"{professor.nombre_facultad} - {professor.profesor} "
                f"<{professor.correo}>"
            )
        )
        self.fields["id_programa_asignatura"].choices = (
            self._programa_asignatura_choices(selected_facultad)
        )

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        if homologacion is not None:
            self.fields["id_estudiante"].disabled = True
            self.fields["id_estudiante"].initial = homologacion.id_estudiante
            self.fields["id_profesor_evaluador"].initial = (
                homologacion.id_profesor_evaluador
            )
            self.fields["asignatura_origen"].initial = homologacion.asignatura_origen
            self.fields["institucion_origen"].initial = homologacion.institucion_origen
            self.fields["id_programa_asignatura"].initial = str(
                homologacion.id_programa_asignatura,
            )
            self.fields["fecha_solicitud"].initial = homologacion.fecha_solicitud
            self.fields[
                "estado_homologacion"
            ].initial = homologacion.estado_homologacion

    def _programa_asignatura_choices(self, selected_facultad=None):
        where = ["pa.estado = 'Activa'"]
        params = []
        if selected_facultad:
            where.append("pa.id_facultad = %s")
            params.append(selected_facultad)
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

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("id_estudiante")
        professor = cleaned_data.get("id_profesor_evaluador")
        programa_asignatura = cleaned_data.get("id_programa_asignatura")

        if student and professor and student.id_facultad != professor.id_facultad:
            raise ValidationError("El evaluador debe pertenecer a la facultad.")

        if student and programa_asignatura:
            rows = _choice_rows(
                """
                select id_facultad
                from reportes.vw_programa_asignatura_global
                where id_programa_asignatura = %s
                """,
                [programa_asignatura],
            )
            if not rows:
                raise ValidationError("La asignatura destino no existe.")
            if rows[0][0] != student.id_facultad:
                raise ValidationError(
                    "La asignatura destino no pertenece a la facultad.",
                )

        return cleaned_data

    def save(self):
        if self.homologacion is None:
            return create_homologacion(
                id_profesor_evaluador=self.cleaned_data["id_profesor_evaluador"].pk,
                id_estudiante=self.cleaned_data["id_estudiante"].pk,
                asignatura_origen=self.cleaned_data["asignatura_origen"],
                institucion_origen=self.cleaned_data["institucion_origen"],
                id_programa_asignatura=self.cleaned_data["id_programa_asignatura"],
                fecha_solicitud=self.cleaned_data["fecha_solicitud"],
                estado_homologacion=self.cleaned_data["estado_homologacion"],
            )

        return update_homologacion(
            id_homologacion=self.homologacion.id_homologacion,
            id_facultad=self.homologacion.id_facultad,
            id_profesor_evaluador=self.cleaned_data["id_profesor_evaluador"].pk,
            id_estudiante=self.cleaned_data["id_estudiante"].pk,
            asignatura_origen=self.cleaned_data["asignatura_origen"],
            institucion_origen=self.cleaned_data["institucion_origen"],
            id_programa_asignatura=self.cleaned_data["id_programa_asignatura"],
            fecha_solicitud=self.cleaned_data["fecha_solicitud"],
            estado_homologacion=self.cleaned_data["estado_homologacion"],
            observacion=self.homologacion.observacion,
            fecha_respuesta=self.homologacion.fecha_respuesta,
            nota_obtenida=self.homologacion.nota_obtenida,
        )


class HomologacionAssignEvaluatorForm(forms.Form):
    id_profesor_evaluador = forms.ModelChoiceField(
        label="Profesor evaluador",
        queryset=ProfesorDetalle.objects.none(),
    )

    def __init__(self, *args, homologacion, **kwargs):
        super().__init__(*args, **kwargs)
        self.homologacion = homologacion
        self.fields["id_profesor_evaluador"].queryset = (
            ProfesorDetalle.objects.filter(id_facultad=homologacion.id_facultad)
            .order_by("profesor")
        )
        self.fields["id_profesor_evaluador"].label_from_instance = (
            lambda professor: f"{professor.nombre_facultad} - {professor.profesor}"
        )
        self.fields["id_profesor_evaluador"].initial = (
            homologacion.id_profesor_evaluador
        )
        self.fields["id_profesor_evaluador"].widget.attrs.setdefault(
            "class",
            "form-control",
        )

    def save(self):
        return asignar_evaluador_homologacion(
            id_homologacion=self.homologacion.id_homologacion,
            id_facultad=self.homologacion.id_facultad,
            id_profesor_evaluador=self.cleaned_data["id_profesor_evaluador"].pk,
        )


class HomologacionEvaluateForm(forms.Form):
    estado_homologacion = forms.ChoiceField(
        label="Estado",
        choices=EVALUATION_STATUS_CHOICES,
    )
    observacion = forms.CharField(
        label="Observacion",
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    fecha_respuesta = forms.DateField(
        label="Fecha de respuesta",
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    nota_obtenida = forms.DecimalField(
        label="Nota obtenida",
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=5,
        required=False,
    )

    def __init__(self, *args, homologacion, **kwargs):
        super().__init__(*args, **kwargs)
        self.homologacion = homologacion
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["estado_homologacion"].initial = homologacion.estado_homologacion
        self.fields["observacion"].initial = homologacion.observacion
        self.fields["fecha_respuesta"].initial = (
            homologacion.fecha_respuesta or timezone.localdate()
        )
        self.fields["nota_obtenida"].initial = homologacion.nota_obtenida

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("estado_homologacion") == "Aprobada"
            and cleaned_data.get("nota_obtenida") is None
        ):
            raise ValidationError("La nota obtenida es obligatoria para aprobar.")
        return cleaned_data

    def save(self):
        return evaluar_homologacion(
            id_homologacion=self.homologacion.id_homologacion,
            id_facultad=self.homologacion.id_facultad,
            estado_homologacion=self.cleaned_data["estado_homologacion"],
            observacion=self.cleaned_data.get("observacion") or None,
            fecha_respuesta=self.cleaned_data["fecha_respuesta"],
            nota_obtenida=self.cleaned_data.get("nota_obtenida"),
        )
