from pytest import mark

from bpystubgen.parser import parse_type


@mark.parametrize("text", ("", "  ", "\n"))
def test_parse_empty(text: str):
    assert not parse_type(text)


@mark.parametrize("text", (
        "str",
        "string",
        "strings",
        "String",
        "Strings",
        "string (read only)",
        "String, default \"\", (never None)"
))
def test_parse_string(text: str):
    assert parse_type(text) == "str"


@mark.parametrize("text", (
        "bool",
        "boolean",
        "booleans",
        "Boolean",
        "Booleans",
        "boolean (never None)",
        "boolean, default \"\", (never None)"
))
def test_parse_boolean(text: str):
    assert parse_type(text) == "bool"


@mark.parametrize("text", (
        "int",
        "integer",
        "Integers",
        "unsigned int",
        "unsigned ints",
        "unsigned integer",
        "unsigned integers",
        "int (must be one of 1, 2, 4, 8, 16)",
        "integer (one of :ref:`these constants <armaturechannel-constants-rotation-mode>`)",
        "int in [-32768, 32767], default 0",
        "int in [0, 10000], default 0",
        "int in [0, 10000].",
        "int in [-inf, inf], default 0, (readonly)",
        "int from 0 to 5",
        "integer from 0 to 5"
))
def test_parse_integer(text: str):
    assert parse_type(text) == "int"


@mark.parametrize("text", (
        "float",
        "floats",
        "Floats",
        "double",
        "Double",
        "float in [0, 1], default 1.0",
        "float in [0, 1].",
        "Double in [0, 6.28319], default 6.28319",
        "float in [-inf, inf], default 0.0",
        "float in [-31.4159, 31.4159], default 0.0"
))
def test_parse_float(text: str):
    assert parse_type(text) == "float"


@mark.parametrize("text", (
        ":class:`bge.types.KX_GameObject`",
        ":class:`~bge.types.KX_GameObject`",
        ":class:`!bge.types.KX_GameObject`",
        ":class:`~bge.types.KX_GameObject`.",
        ":class:`bge.types.KX_GameObject`, (read only)",
        ":class:`~bge.types.KX_GameObject` subclass",
        ":class:`Game Object <bge.types.KX_GameObject>`, (read only)"
))
def test_parse_references(text: str):
    assert parse_type(text) == "bge.types.KX_GameObject"


def test_parse_misc_types():
    assert parse_type("type") == "typing.Type"
    assert parse_type("Type") == "typing.Type"
    assert parse_type("class") == "typing.Type"
    assert parse_type("Class") == "typing.Type"
    assert parse_type("function") == "typing.Callable"
    assert parse_type("Function") == "typing.Callable"
    assert parse_type("callable") == "typing.Callable"
    assert parse_type("Callable") == "typing.Callable"


@mark.parametrize("args", (
        ("list", "typing.Any"),
        ("List", "typing.Any"),
        ("list (read only)", "typing.Any"),
        ("list, (read only)", "typing.Any"),
        ("list of integer", "int"),
        ("list of ints.", "int"),
        ("list of floats [x, y, z]", "float"),
        ("list of :class:`~bge.types.SCA_ISensor`", "bge.types.SCA_ISensor"),
        ("list of :class:`bge.types.KX_Scene`", "bge.types.KX_Scene"),
        ("list of :class:`mathutils.Vector`'s", "mathutils.Vector"),
        ("list of :class:`!freestyle.types.ViewShape` objects", "freestyle.types.ViewShape"),
        ("list of :class:`~bge.types.KX_BlenderMaterial` type", "bge.types.KX_BlenderMaterial"),
        ("list of :class:`KX_MeshProxy <bge.types.KX_MeshProxy>`", "bge.types.KX_MeshProxy"),
        ("list of tuples", "typing.Tuple[typing.Any, ...]"),
        ("list of :class:`BMLoop` tuples", "typing.Tuple[BMLoop, ...]"),
        ("list (vector of 3 floats)", "float"),
        ("list (normalized vector of 3 floats)", "float"),
        ("list (vector of 2 integers from 0 to 2)", "int"),
        ("list [str]", "str"),
        ("list [:class:`~bge.types.KX_GameObject`]", "bge.types.KX_GameObject"),
        ("list [float], len(getSpectrum()) == 512", "float")
))
def test_parse_list(args):
    (text, expected) = args
    assert parse_type(text) == f"typing.List[{expected}]"


def test_bpy_prop_collection():
    result = parse_type(":class:`bpy_prop_collection` of :class:`LodLevel`")
    assert result == f"typing.Union[typing.Sequence[LodLevel], typing.Mapping[str, LodLevel]]"


@mark.parametrize("args", (
        ("int array of 4 items", "int, int, int, int"),
        ("boolean array of 3 items, default (False, False, False)", "bool, bool, bool"),
        ("float array of 2 items in [-inf, inf], (optional)", "float, float"),
        ("int array of 8 items", "int, ..."),
        ("float multi-dimensional array of 3 * 2 items in [-1, 1]",
         "typing.Tuple[float, float], typing.Tuple[float, float], typing.Tuple[float, float]"),
        ("float multi-dimensional array of 3 * 8 items in [-1, 1]",
         "typing.Tuple[float, ...], typing.Tuple[float, ...], typing.Tuple[float, ...]"),
        ("float multi-dimensional array of 8 * 3 items in [-1, 1]",
         "typing.Tuple[float, float, float], ...")
))
def test_parse_array(args):
    (text, expected) = args
    assert parse_type(text) == f"typing.Tuple[{expected}]"


@mark.parametrize("args", (
        (
                "dict[:ref:`keycode<mouse-keys>`, :class:`~bge.types.SCA_InputEvent`]",
                "typing.Any",
                "bge.types.SCA_InputEvent"
        ),
        (
                "dict[:ref:`keycode<keyboard-keys>`, :class:`SCA_InputEvent <bge.types.SCA_InputEvent>`]",
                "typing.Any",
                "bge.types.SCA_InputEvent"
        ),
        (
                "dict (string, :class:`~bge.types.SCA_InputEvent`)",
                "str",
                "bge.types.SCA_InputEvent"
        ),
        (
                "dictionary[:ref:`keycode<mouse-keys>`,:ref:`status<input-status>`]",
                "typing.Any",
                "typing.Any"
        )
))
def test_dictionary(args):
    (text, key, value) = args
    assert parse_type(text) == f"typing.Dict[{key}, {value}]"


@mark.parametrize("text", (
        "vector [x, y, z]",
        "Vector [x, y, z]",
        "Vector((x, y, z))",
        "vector [sizeX, sizeY, sizeZ]",
        "3d vector",
        "2d Vector"
))
def test_parse_vector(text):
    assert parse_type(text) == "mathutils.Vector"


def test_parse_simple_container():
    assert parse_type("array") == "typing.Tuple[typing.Any, ...]"
    assert parse_type("Array") == "typing.Tuple[typing.Any, ...]"
    assert parse_type("tuple") == "typing.Tuple[typing.Any, ...]"
    assert parse_type("Tuple") == "typing.Tuple[typing.Any, ...]"
    assert parse_type("sequence") == "typing.Sequence[typing.Any]"
    assert parse_type("Sequence") == "typing.Sequence[typing.Any]"
    assert parse_type("dict") == "typing.Dict[str, typing.Any]"
