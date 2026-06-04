from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from contextlib import nullcontext
from dataclasses import dataclass
from uuid import NAMESPACE_URL, UUID, uuid5

from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError, connection, transaction

from apps.academica.distributed_write import (
    FACULTAD_TO_FDW,
    get_fdw_schema_for_facultad,
)

PROGRAM_TABLE = '"institucional"."programa_academico"'
SUBJECT_TABLE = '"institucional"."asignatura"'
RELATION_TABLE = "programa_asignatura"
PREREQ_TABLE = "pre_requisito"


@dataclass(frozen=True)
class ProgramSpec:
    id: str
    faculty_id: str
    name: str

    @property
    def level(self) -> str:
        if self.name.startswith("Tecnologia"):
            return "Tecnologico"
        return "Pregrado"


@dataclass(frozen=True)
class SubjectSpec:
    code: str
    name: str
    credits: int
    theory_hours: int
    practice_hours: int

    @property
    def homologable(self) -> bool:
        return self.practice_hours == 0


@dataclass(frozen=True)
class RelationSpec:
    program_id: str
    faculty_id: str
    subject_code: str
    semester: int
    subject_type: str

    @property
    def id(self) -> UUID:
        return uuid5(
            NAMESPACE_URL,
            f"condor-caido:programa-asignatura:{self.program_id}:{self.subject_code}",
        )


@dataclass(frozen=True)
class PrereqSpec:
    program_id: str
    faculty_id: str
    subject_code: str
    required_subject_code: str

    @property
    def id(self) -> UUID:
        return uuid5(
            NAMESPACE_URL,
            (
                "condor-caido:pre-requisito:"
                f"{self.program_id}:{self.subject_code}:{self.required_subject_code}"
            ),
        )


PROGRAMS = [
    ProgramSpec("FING-SIS", "FING", "Ingenieria de Sistemas"),
    ProgramSpec("FING-IND", "FING", "Ingenieria Industrial"),
    ProgramSpec("FING-ELE", "FING", "Ingenieria Electronica"),
    ProgramSpec("FING-CAT", "FING", "Ingenieria Catastral y Geodesia"),
    ProgramSpec("FING-CIV", "FING", "Ingenieria Civil"),
    ProgramSpec("FTEC-TSD", "FTEC", "Tecnologia en Sistematizacion de Datos"),
    ProgramSpec(
        "FTEC-GPI",
        "FTEC",
        "Tecnologia en Gestion de la Produccion Industrial",
    ),
    ProgramSpec("FTEC-TEL", "FTEC", "Ingenieria en Telecomunicaciones"),
    ProgramSpec("FTEC-MEC", "FTEC", "Ingenieria Mecanica"),
    ProgramSpec("FTEC-ELEC", "FTEC", "Tecnologia en Electricidad"),
    ProgramSpec("FCE-MAT", "FCE", "Licenciatura en Matematicas"),
    ProgramSpec("FCE-BIO", "FCE", "Licenciatura en Biologia"),
    ProgramSpec("FCE-FIS", "FCE", "Licenciatura en Fisica"),
    ProgramSpec("FCE-SOC", "FCE", "Licenciatura en Ciencias Sociales"),
    ProgramSpec("FCE-HLC", "FCE", "Licenciatura en Humanidades y Lengua Castellana"),
    ProgramSpec("FMA-IAM", "FMA", "Ingenieria Ambiental"),
    ProgramSpec("FMA-ADM", "FMA", "Administracion Ambiental"),
    ProgramSpec("FMA-SAN", "FMA", "Ingenieria Sanitaria"),
    ProgramSpec("FMA-GAM", "FMA", "Tecnologia en Gestion Ambiental"),
    ProgramSpec("FMA-FOR", "FMA", "Ingenieria Forestal"),
    ProgramSpec("FART-MUS", "FART", "Artes Musicales"),
    ProgramSpec("FART-ESC", "FART", "Artes Escenicas"),
    ProgramSpec("FART-PLV", "FART", "Artes Plasticas y Visuales"),
    ProgramSpec("FART-DAN", "FART", "Arte Danzario"),
    ProgramSpec("FART-GCA", "FART", "Gestion Cultural y Artistica"),
]


SHARED_SUBJECTS = {
    "GEN-CALDIF": SubjectSpec("GEN-CALDIF", "Calculo Diferencial", 3, 48, 0),
    "GEN-CALINT": SubjectSpec("GEN-CALINT", "Calculo Integral", 3, 48, 0),
    "GEN-ALGLIN": SubjectSpec("GEN-ALGLIN", "Algebra Lineal", 3, 48, 0),
    "GEN-ESTBAS": SubjectSpec("GEN-ESTBAS", "Estadistica Basica", 3, 48, 0),
    "GEN-ESTAPL": SubjectSpec("GEN-ESTAPL", "Estadistica Aplicada", 3, 32, 16),
    "GEN-ETIPRO": SubjectSpec("GEN-ETIPRO", "Etica Profesional", 2, 32, 0),
    "GEN-METINV": SubjectSpec("GEN-METINV", "Metodologia de Investigacion", 2, 32, 0),
    "GEN-PROG1": SubjectSpec("GEN-PROG1", "Programacion I", 3, 32, 32),
    "GEN-PROG2": SubjectSpec("GEN-PROG2", "Programacion II", 3, 32, 32),
    "GEN-BDD": SubjectSpec("GEN-BDD", "Bases de Datos", 3, 32, 32),
    "GEN-REDES": SubjectSpec("GEN-REDES", "Fundamentos de Redes", 3, 32, 32),
    "GEN-REDES2": SubjectSpec("GEN-REDES2", "Redes II", 3, 32, 32),
}


PROGRAM_SPECIFIC_SUBJECTS = {
    "FING-SIS": [
        SubjectSpec("SIS-ARQSW", "Arquitectura de Software", 3, 32, 32),
        SubjectSpec("SIS-IA", "Inteligencia Artificial", 3, 32, 32),
        SubjectSpec("SIS-SEG", "Seguridad Informatica", 3, 32, 32),
    ],
    "FING-IND": [
        SubjectSpec("IND-INVOP", "Investigacion de Operaciones", 3, 48, 0),
        SubjectSpec("IND-PROD", "Gestion de Produccion", 3, 32, 16),
        SubjectSpec("IND-CAL", "Control de Calidad", 3, 32, 16),
        SubjectSpec("IND-LOG", "Logistica Industrial", 3, 32, 16),
    ],
    "FING-ELE": [
        SubjectSpec("ELE-CIRC", "Circuitos Electricos", 3, 32, 32),
        SubjectSpec("ELE-DIG", "Electronica Digital", 3, 32, 32),
        SubjectSpec("ELE-SEN", "Sistemas Embebidos", 3, 32, 32),
        SubjectSpec("ELE-COM", "Comunicaciones Analogicas", 3, 32, 16),
    ],
    "FING-CAT": [
        SubjectSpec("CAT-TOPO", "Topografia", 3, 32, 32),
        SubjectSpec("CAT-GEOD", "Geodesia", 3, 32, 32),
        SubjectSpec("CAT-SIG", "Sistemas de Informacion Geografica", 3, 32, 32),
        SubjectSpec("CAT-CATA", "Catastro Multiproposito", 3, 32, 16),
    ],
    "FING-CIV": [
        SubjectSpec("CIV-ESTR", "Estructuras", 3, 32, 32),
        SubjectSpec("CIV-SUEL", "Mecanica de Suelos", 3, 32, 32),
        SubjectSpec("CIV-HIDR", "Hidraulica", 3, 32, 32),
        SubjectSpec("CIV-VIAS", "Diseno de Vias", 3, 32, 16),
    ],
    "FTEC-TSD": [
        SubjectSpec("TSD-WEB", "Desarrollo Web", 3, 32, 32),
        SubjectSpec("TSD-SOP", "Sistemas Operativos", 3, 32, 32),
        SubjectSpec("TSD-MOV", "Aplicaciones Moviles", 3, 32, 32),
    ],
    "FTEC-GPI": [
        SubjectSpec("GPI-PROC", "Procesos Industriales", 3, 32, 16),
        SubjectSpec("GPI-COST", "Costos de Produccion", 3, 48, 0),
        SubjectSpec("GPI-MANT", "Gestion de Mantenimiento", 3, 32, 16),
        SubjectSpec("GPI-PLANE", "Planeacion de Produccion", 3, 32, 16),
    ],
    "FTEC-TEL": [
        SubjectSpec("TEL-SENA", "Senales y Sistemas", 3, 48, 0),
        SubjectSpec("TEL-ANTE", "Antenas y Propagacion", 3, 32, 16),
        SubjectSpec("TEL-FIBRA", "Comunicaciones por Fibra Optica", 3, 32, 16),
    ],
    "FTEC-MEC": [
        SubjectSpec("MEC-TERMO", "Termodinamica", 3, 48, 0),
        SubjectSpec("MEC-MAT", "Materiales de Ingenieria", 3, 32, 16),
        SubjectSpec("MEC-DIS", "Diseno Mecanico", 3, 32, 32),
        SubjectSpec("MEC-MANU", "Manufactura", 3, 32, 32),
    ],
    "FTEC-ELEC": [
        SubjectSpec("TELEC-CIRC", "Circuitos Electricos Aplicados", 3, 32, 32),
        SubjectSpec("TELEC-INST", "Instalaciones Electricas", 3, 32, 32),
        SubjectSpec("TELEC-MAQ", "Maquinas Electricas", 3, 32, 32),
        SubjectSpec("TELEC-POT", "Sistemas de Potencia", 3, 32, 16),
    ],
    "FCE-MAT": [
        SubjectSpec("MAT-GEOM", "Geometria Euclidiana", 3, 48, 0),
        SubjectSpec("MAT-DID", "Didactica de la Matematica", 3, 32, 16),
        SubjectSpec("MAT-NUM", "Metodos Numericos", 3, 32, 32),
    ],
    "FCE-BIO": [
        SubjectSpec("BIO-CEL", "Biologia Celular", 3, 32, 32),
        SubjectSpec("BIO-ECO", "Ecologia", 3, 32, 32),
        SubjectSpec("BIO-GEN", "Genetica", 3, 32, 32),
    ],
    "FCE-FIS": [
        SubjectSpec("FIS-MEC", "Mecanica Clasica", 3, 48, 0),
        SubjectSpec("FIS-ELEC", "Electricidad y Magnetismo", 3, 32, 32),
        SubjectSpec("FIS-MOD", "Fisica Moderna", 3, 48, 0),
    ],
    "FCE-SOC": [
        SubjectSpec("SOC-HCOL", "Historia de Colombia", 3, 48, 0),
        SubjectSpec("SOC-GEO", "Geografia Humana", 3, 48, 0),
        SubjectSpec("SOC-POL", "Pensamiento Politico", 3, 48, 0),
    ],
    "FCE-HLC": [
        SubjectSpec("HLC-LING", "Linguistica General", 3, 48, 0),
        SubjectSpec("HLC-LITCOL", "Literatura Colombiana", 3, 48, 0),
        SubjectSpec("HLC-LECT", "Procesos de Lectura y Escritura", 3, 32, 16),
    ],
    "FMA-IAM": [
        SubjectSpec("IAM-EIA", "Evaluacion de Impacto Ambiental", 3, 32, 16),
        SubjectSpec("IAM-HIDRO", "Hidrologia Ambiental", 3, 32, 32),
        SubjectSpec("IAM-GRES", "Gestion de Residuos", 3, 32, 16),
    ],
    "FMA-ADM": [
        SubjectSpec("ADM-ECOAMB", "Economia Ambiental", 3, 48, 0),
        SubjectSpec("ADM-POLAMB", "Politica Ambiental", 3, 48, 0),
        SubjectSpec("ADM-PROAMB", "Proyectos Ambientales", 3, 32, 16),
    ],
    "FMA-SAN": [
        SubjectSpec("SAN-AGUA", "Tratamiento de Agua", 3, 32, 32),
        SubjectSpec("SAN-RES", "Residuos Solidos", 3, 32, 16),
        SubjectSpec("SAN-SALUD", "Salud Publica Ambiental", 3, 48, 0),
    ],
    "FMA-GAM": [
        SubjectSpec("GAM-EDU", "Educacion Ambiental", 3, 32, 16),
        SubjectSpec("GAM-ORD", "Ordenamiento Ambiental", 3, 48, 0),
        SubjectSpec("GAM-AUD", "Auditoria Ambiental", 3, 32, 16),
    ],
    "FMA-FOR": [
        SubjectSpec("FOR-DEND", "Dendrologia", 3, 32, 32),
        SubjectSpec("FOR-SILV", "Silvicultura", 3, 32, 32),
        SubjectSpec("FOR-MANE", "Manejo de Bosques", 3, 32, 16),
    ],
    "FART-MUS": [
        SubjectSpec("MUS-SOLF", "Solfeo", 3, 32, 32),
        SubjectSpec("MUS-ARM", "Armonia", 3, 48, 0),
        SubjectSpec("MUS-ENS", "Ensamble Musical", 3, 16, 48),
    ],
    "FART-ESC": [
        SubjectSpec("ESC-ACT", "Actuacion", 3, 16, 48),
        SubjectSpec("ESC-DIR", "Direccion Escenica", 3, 32, 32),
        SubjectSpec("ESC-VOZ", "Voz y Movimiento", 3, 16, 48),
    ],
    "FART-PLV": [
        SubjectSpec("PLV-DIB", "Dibujo Artistico", 3, 16, 48),
        SubjectSpec("PLV-PINT", "Pintura", 3, 16, 48),
        SubjectSpec("PLV-ESC", "Escultura", 3, 16, 48),
    ],
    "FART-DAN": [
        SubjectSpec("DAN-TEC", "Tecnica de Danza", 3, 16, 48),
        SubjectSpec("DAN-COMP", "Composicion Coreografica", 3, 16, 48),
        SubjectSpec("DAN-CUE", "Cuerpo y Movimiento", 3, 16, 48),
    ],
    "FART-GCA": [
        SubjectSpec("GCA-GEST", "Gestion de Proyectos Culturales", 3, 32, 16),
        SubjectSpec("GCA-PATR", "Patrimonio Cultural", 3, 48, 0),
        SubjectSpec("GCA-PROD", "Produccion Artistica", 3, 32, 16),
    ],
}


DEFAULT_PLAN = [
    ("GEN-CALDIF", 1, "Obligatoria"),
    ("GEN-ALGLIN", 1, "Obligatoria"),
    ("GEN-PROG1", 2, "Obligatoria"),
    ("GEN-ESTBAS", 2, "Obligatoria"),
    ("GEN-PROG2", 3, "Obligatoria"),
    ("GEN-BDD", 3, "Obligatoria"),
    ("GEN-ETIPRO", 4, "Obligatoria"),
    ("GEN-METINV", 4, "Obligatoria"),
    ("GEN-ESTAPL", 5, "Obligatoria"),
    ("PROGRAM-0", 5, "Obligatoria"),
    ("PROGRAM-1", 6, "Obligatoria"),
    ("PROGRAM-2", 6, "Electiva"),
]


PROGRAM_PLAN_OVERRIDES = {
    "FING-SIS": [
        ("GEN-CALDIF", 1, "Obligatoria"),
        ("GEN-ALGLIN", 1, "Obligatoria"),
        ("GEN-PROG1", 2, "Obligatoria"),
        ("GEN-PROG2", 2, "Obligatoria"),
        ("GEN-BDD", 3, "Obligatoria"),
        ("GEN-REDES", 3, "Obligatoria"),
        ("SIS-ARQSW", 4, "Obligatoria"),
        ("SIS-SEG", 4, "Obligatoria"),
        ("GEN-REDES2", 5, "Obligatoria"),
        ("GEN-ETIPRO", 5, "Obligatoria"),
        ("SIS-IA", 6, "Electiva"),
    ],
    "FTEC-TSD": [
        ("GEN-PROG1", 1, "Obligatoria"),
        ("GEN-ALGLIN", 1, "Obligatoria"),
        ("GEN-PROG2", 2, "Obligatoria"),
        ("GEN-BDD", 2, "Obligatoria"),
        ("GEN-REDES", 3, "Obligatoria"),
        ("TSD-WEB", 3, "Obligatoria"),
        ("TSD-SOP", 4, "Obligatoria"),
        ("GEN-ETIPRO", 4, "Obligatoria"),
        ("TSD-MOV", 5, "Electiva"),
        ("GEN-METINV", 5, "Obligatoria"),
    ],
    "FTEC-TEL": [
        ("GEN-CALDIF", 1, "Obligatoria"),
        ("GEN-ALGLIN", 1, "Obligatoria"),
        ("GEN-REDES", 2, "Obligatoria"),
        ("GEN-REDES2", 3, "Obligatoria"),
        ("TEL-SENA", 3, "Obligatoria"),
        ("TEL-ANTE", 4, "Obligatoria"),
        ("TEL-FIBRA", 5, "Obligatoria"),
        ("GEN-ESTBAS", 5, "Obligatoria"),
        ("GEN-ETIPRO", 6, "Obligatoria"),
        ("GEN-METINV", 6, "Electiva"),
    ],
    "FCE-MAT": [
        ("GEN-CALDIF", 1, "Obligatoria"),
        ("GEN-ALGLIN", 1, "Obligatoria"),
        ("GEN-CALINT", 2, "Obligatoria"),
        ("GEN-ESTBAS", 2, "Obligatoria"),
        ("MAT-GEOM", 3, "Obligatoria"),
        ("MAT-NUM", 4, "Obligatoria"),
        ("MAT-DID", 5, "Obligatoria"),
        ("GEN-METINV", 5, "Obligatoria"),
        ("GEN-ETIPRO", 6, "Obligatoria"),
        ("GEN-ESTAPL", 6, "Electiva"),
    ],
}


PREREQ_PAIRS = [
    ("GEN-PROG2", "GEN-PROG1"),
    ("GEN-BDD", "GEN-PROG2"),
    ("GEN-REDES2", "GEN-REDES"),
    ("GEN-CALINT", "GEN-CALDIF"),
    ("GEN-ESTAPL", "GEN-ESTBAS"),
]


class BaseCommandWithSeedData(BaseCommand):
    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra que registros se insertarian sin escribir en base de datos.",
        )
        group.add_argument(
            "--apply",
            action="store_true",
            help="Inserta de forma idempotente el catalogo academico demo.",
        )

    def handle(self, *args, **options):
        apply = options["apply"]
        subjects_by_code, relations, prereqs = build_catalog()

        try:
            with connection.cursor() as cursor:
                self._validate_database_shape(cursor)
                result = self._seed(
                    cursor=cursor,
                    apply=apply,
                    subjects=subjects_by_code.values(),
                    relations=relations,
                    prereqs=prereqs,
                )
        except OperationalError as exc:
            raise CommandError(
                "No se pudo conectar a PostgreSQL. Verifica que sga_central "
                "este arriba antes de ejecutar el seed.",
            ) from exc

        mode = "APPLY" if apply else "DRY-RUN"
        self.stdout.write(self.style.SUCCESS(f"Seed catalogo academico demo ({mode})"))
        for key, value in result.items():
            self.stdout.write(f"- {key}: {value}")


class Command(BaseCommandWithSeedData):
    help = "Puebla programas, asignaturas y planes academicos demo sin duplicar datos."

    def _validate_database_shape(self, cursor):
        cursor.execute(
            """
            select id_facultad
            from institucional.facultad
            where id_facultad = any(%s)
            """,
            [list(FACULTAD_TO_FDW)],
        )
        found_faculties = {row[0] for row in cursor.fetchall()}
        missing_faculties = set(FACULTAD_TO_FDW) - found_faculties
        if missing_faculties:
            missing = ", ".join(sorted(missing_faculties))
            raise CommandError(f"No existen las facultades requeridas: {missing}")

        missing_tables = []
        for faculty_id in FACULTAD_TO_FDW:
            schema = get_fdw_schema_for_facultad(faculty_id)
            if not table_exists(cursor, schema, RELATION_TABLE):
                missing_tables.append(f"{schema}.{RELATION_TABLE}")
        if missing_tables:
            raise CommandError(
                "No existen las tablas FDW requeridas: "
                + ", ".join(sorted(missing_tables)),
            )

    def _seed(self, *, cursor, apply, subjects, relations, prereqs):
        context = transaction.atomic() if apply else nullcontext()
        with context:
            result = Counter()
            result.update(self._seed_programs(cursor, apply))
            result.update(self._seed_subjects(cursor, apply, subjects))
            result.update(self._seed_relations(cursor, apply, relations))
            result.update(self._seed_prereqs(cursor, apply, prereqs, relations))
            result.update(self._final_counts(cursor))
            return dict(result)

    def _seed_programs(self, cursor, apply):
        result = Counter()
        cursor.execute(
            """
            select id_programa_academico
            from institucional.programa_academico
            where id_programa_academico = any(%s)
            """,
            [[program.id for program in PROGRAMS]],
        )
        existing = {row[0] for row in cursor.fetchall()}

        for program in PROGRAMS:
            if program.id in existing:
                result["programas_omitidos_duplicados"] += 1
                continue
            result["programas_por_crear" if not apply else "programas_creados"] += 1
            if apply:
                cursor.execute(
                    f"""
                    insert into {PROGRAM_TABLE} (
                        id_programa_academico,
                        id_facultad,
                        nombre_programa,
                        estado,
                        modalidad,
                        nivel_formacion
                    )
                    values (%s, %s, %s, %s, %s, %s)
                    """,
                    [
                        program.id,
                        program.faculty_id,
                        program.name,
                        "Activo",
                        "Presencial",
                        program.level,
                    ],
                )
        return result

    def _seed_subjects(self, cursor, apply, subjects):
        result = Counter()
        subject_list = list(subjects)
        cursor.execute(
            """
            select cod_asignatura
            from institucional.asignatura
            where cod_asignatura = any(%s)
            """,
            [[subject.code for subject in subject_list]],
        )
        existing = {row[0] for row in cursor.fetchall()}

        for subject in subject_list:
            if subject.code in existing:
                result["asignaturas_omitidas_duplicadas"] += 1
                continue
            result["asignaturas_por_crear" if not apply else "asignaturas_creadas"] += 1
            if apply:
                cursor.execute(
                    f"""
                    insert into {SUBJECT_TABLE} (
                        cod_asignatura,
                        nombre_asignatura,
                        creditos,
                        estado,
                        horas_teoria,
                        horas_pract,
                        homologable
                    )
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        subject.code,
                        subject.name,
                        subject.credits,
                        "Activa",
                        subject.theory_hours,
                        subject.practice_hours,
                        subject.homologable,
                    ],
                )
        return result

    def _seed_relations(self, cursor, apply, relations):
        result = Counter()
        by_schema = relations_by_schema(relations)

        for schema, schema_relations in by_schema.items():
            table = quote_table(schema, RELATION_TABLE)
            existing = fetch_relation_pairs(cursor, table, schema_relations)
            for relation in schema_relations:
                pair = (relation.program_id, relation.subject_code)
                if pair in existing:
                    result["relaciones_omitidas_duplicadas"] += 1
                    continue
                key = "relaciones_por_crear" if not apply else "relaciones_creadas"
                result[key] += 1
                if apply:
                    cursor.execute(
                        f"""
                        insert into {table} (
                            id_programa_asignatura,
                            id_facultad,
                            id_programa_academico,
                            cod_asignatura,
                            semestre_sugerido,
                            tipo_asignatura,
                            estado
                        )
                        values (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            relation.id,
                            relation.faculty_id,
                            relation.program_id,
                            relation.subject_code,
                            relation.semester,
                            relation.subject_type,
                            "Activa",
                        ],
                    )
        return result

    def _seed_prereqs(self, cursor, apply, prereqs, relations):
        result = Counter()
        by_schema = prereqs_by_schema(prereqs)
        relation_ids = fetch_relation_ids(cursor, relations)

        for schema, schema_prereqs in by_schema.items():
            if not table_exists(cursor, schema, PREREQ_TABLE):
                result[f"prerrequisitos_omitidos_sin_tabla_{schema}"] += len(
                    schema_prereqs,
                )
                continue
            columns = table_columns(cursor, schema, PREREQ_TABLE)
            expected = {
                "id_pre_requisito",
                "id_programa_academico",
                "id_programa_asignatura",
                "id_programa_asignatura_requisito",
            }
            if not expected.issubset(columns):
                result[f"prerrequisitos_omitidos_columnas_{schema}"] += len(
                    schema_prereqs,
                )
                continue

            table = quote_table(schema, PREREQ_TABLE)
            existing = fetch_prereq_pairs(cursor, table, schema_prereqs)
            includes_faculty = "id_facultad" in columns

            for prereq in schema_prereqs:
                relation_id = relation_ids.get((prereq.program_id, prereq.subject_code))
                required_id = relation_ids.get(
                    (prereq.program_id, prereq.required_subject_code),
                )
                if not relation_id or not required_id:
                    result["prerrequisitos_omitidos_sin_relacion"] += 1
                    continue
                pair = (prereq.program_id, relation_id, required_id)
                if pair in existing or relation_id == required_id:
                    result["prerrequisitos_omitidos_duplicados"] += 1
                    continue
                key = (
                    "prerrequisitos_por_crear"
                    if not apply
                    else "prerrequisitos_creados"
                )
                result[key] += 1
                if apply:
                    insert_prereq(
                        cursor,
                        table=table,
                        prereq=prereq,
                        relation_id=relation_id,
                        required_id=required_id,
                        includes_faculty=includes_faculty,
                    )
        return result

    def _final_counts(self, cursor):
        result = Counter()
        cursor.execute("select count(*) from institucional.programa_academico")
        result["total_programas_institucional"] = cursor.fetchone()[0]
        cursor.execute("select count(*) from institucional.asignatura")
        result["total_asignaturas_institucional"] = cursor.fetchone()[0]

        for faculty_id, schema in FACULTAD_TO_FDW.items():
            table = quote_table(schema, RELATION_TABLE)
            cursor.execute(f"select count(*) from {table}")
            result[f"total_relaciones_{faculty_id}"] = cursor.fetchone()[0]
        return result


def build_catalog():
    subjects = dict(SHARED_SUBJECTS)
    relations = []
    prereqs = []

    for program in PROGRAMS:
        specific_subjects = PROGRAM_SPECIFIC_SUBJECTS[program.id]
        for subject in specific_subjects:
            subjects[subject.code] = subject

        plan = PROGRAM_PLAN_OVERRIDES.get(
            program.id,
            resolve_default_plan(specific_subjects),
        )
        plan_codes = {subject_code for subject_code, _, _ in plan}
        for subject_code, semester, subject_type in plan:
            relations.append(
                RelationSpec(
                    program_id=program.id,
                    faculty_id=program.faculty_id,
                    subject_code=subject_code,
                    semester=semester,
                    subject_type=subject_type,
                ),
            )

        for subject_code, required_code in PREREQ_PAIRS:
            if subject_code in plan_codes and required_code in plan_codes:
                prereqs.append(
                    PrereqSpec(
                        program_id=program.id,
                        faculty_id=program.faculty_id,
                        subject_code=subject_code,
                        required_subject_code=required_code,
                    ),
                )

    return subjects, relations, prereqs


def resolve_default_plan(specific_subjects):
    specific_codes = [subject.code for subject in specific_subjects]
    plan = []
    for subject_ref, semester, subject_type in DEFAULT_PLAN:
        if subject_ref.startswith("PROGRAM-"):
            index = int(subject_ref.rsplit("-", 1)[1])
            if index >= len(specific_codes):
                continue
            subject_code = specific_codes[index]
        else:
            subject_code = subject_ref
        plan.append((subject_code, semester, subject_type))
    return plan


def relations_by_schema(relations: Iterable[RelationSpec]):
    grouped = defaultdict(list)
    for relation in relations:
        grouped[get_fdw_schema_for_facultad(relation.faculty_id)].append(relation)
    return grouped


def prereqs_by_schema(prereqs: Iterable[PrereqSpec]):
    grouped = defaultdict(list)
    for prereq in prereqs:
        grouped[get_fdw_schema_for_facultad(prereq.faculty_id)].append(prereq)
    return grouped


def quote_table(schema, table):
    if schema not in set(FACULTAD_TO_FDW.values()):
        raise CommandError(f"Esquema FDW no permitido: {schema}")
    return f'"{schema}"."{table}"'


def table_exists(cursor, schema, table):
    cursor.execute("select to_regclass(%s)", [f'"{schema}"."{table}"'])
    return cursor.fetchone()[0] is not None


def table_columns(cursor, schema, table):
    cursor.execute(
        """
        select column_name
        from information_schema.columns
        where table_schema = %s
          and table_name = %s
        """,
        [schema, table],
    )
    return {row[0] for row in cursor.fetchall()}


def fetch_relation_pairs(cursor, table, relations):
    cursor.execute(
        f"""
        select id_programa_academico, cod_asignatura
        from {table}
        where id_programa_academico = any(%s)
          and cod_asignatura = any(%s)
        """,
        [
            [relation.program_id for relation in relations],
            [relation.subject_code for relation in relations],
        ],
    )
    return {(row[0], row[1]) for row in cursor.fetchall()}


def fetch_relation_ids(cursor, relations):
    ids = {}
    for schema, schema_relations in relations_by_schema(relations).items():
        table = quote_table(schema, RELATION_TABLE)
        cursor.execute(
            f"""
            select id_programa_asignatura, id_programa_academico, cod_asignatura
            from {table}
            where id_programa_academico = any(%s)
              and cod_asignatura = any(%s)
            """,
            [
                [relation.program_id for relation in schema_relations],
                [relation.subject_code for relation in schema_relations],
            ],
        )
        ids.update({(row[1], row[2]): row[0] for row in cursor.fetchall()})

        for relation in schema_relations:
            ids.setdefault((relation.program_id, relation.subject_code), relation.id)
    return ids


def fetch_prereq_pairs(cursor, table, prereqs):
    program_ids = [prereq.program_id for prereq in prereqs]
    if not program_ids:
        return set()
    cursor.execute(
        f"""
        select id_programa_academico,
               id_programa_asignatura,
               id_programa_asignatura_requisito
        from {table}
        where id_programa_academico = any(%s)
        """,
        [program_ids],
    )
    return {(row[0], row[1], row[2]) for row in cursor.fetchall()}


def insert_prereq(
    cursor,
    *,
    table,
    prereq,
    relation_id,
    required_id,
    includes_faculty,
):
    if includes_faculty:
        cursor.execute(
            f"""
            insert into {table} (
                id_pre_requisito,
                id_facultad,
                id_programa_academico,
                id_programa_asignatura,
                id_programa_asignatura_requisito
            )
            values (%s, %s, %s, %s, %s)
            """,
            [
                prereq.id,
                prereq.faculty_id,
                prereq.program_id,
                relation_id,
                required_id,
            ],
        )
        return

    cursor.execute(
        f"""
        insert into {table} (
            id_pre_requisito,
            id_programa_academico,
            id_programa_asignatura,
            id_programa_asignatura_requisito
        )
        values (%s, %s, %s, %s)
        """,
        [
            prereq.id,
            prereq.program_id,
            relation_id,
            required_id,
        ],
    )
