import decimal
from os.path import join as fsjoin
from tempfile import TemporaryDirectory

from prefect_yaml.flow.output import Output


def test_output_default():
    with TemporaryDirectory() as tmpdir:
        output_obj = Output(
            name="test",
            metadata={"output-directory": tmpdir},
            description={},
        )

        # Check the output path and its non-existence
        assert output_obj.output_path == fsjoin(tmpdir, "test.pickle")
        assert not output_obj.exists

        # Check its existence after dumping the output
        output_obj.dump(1.0)
        assert output_obj.exists

        # Check its value after loading
        assert 1.0 == output_obj.load()


def test_output_output_directory_override():
    output_obj = Output(
        name="test",
        metadata={"output-directory": "test_dir"},
        description={
            "output-directory": "test2_dir",
        },
    )

    assert output_obj.output_path == fsjoin("test2_dir", "test.pickle")


def _custom_dump(value, output_path, **kwargs):
    value = {"result": value, "error": False}
    from json import dump as json_dump

    with open(output_path, mode="w") as f:
        json_dump(value, f, **kwargs)


def _custom_load(output_path, **kwargs):
    from json import load as json_load

    with open(output_path) as f:
        return {
            "result": json_load(f),
            "success": True,
        }


def test_output_custom_dump_caller():
    with TemporaryDirectory() as tmpdir:
        output_obj = Output(
            name="test",
            metadata={"output-directory": tmpdir},
            description={
                "format": "json",
                "dump-caller": "tests.test_output:_custom_dump",
                "dump-parameters": {
                    "indent": 4,
                },
            },
        )

        assert output_obj.output_path == fsjoin(tmpdir, "test.json")

        # Check its existence after dumping the output
        output_obj.dump(1.0)
        assert output_obj.exists

        # Check its contents
        with open(output_obj.output_path) as f:
            assert (
                f.read()
                == """{
    "result": 1.0,
    "error": false
}"""
            )

        # Check the load value
        assert output_obj.load() == {
            "result": 1.0,
            "error": False,
        }


def test_output_custom_load_caller():
    with TemporaryDirectory() as tmpdir:
        output_obj = Output(
            name="test",
            metadata={"output-directory": tmpdir},
            description={
                "format": "json",
                "load-caller": "tests.test_output:_custom_load",
                "load-parameters": {
                    "parse_float": decimal.Decimal,
                },
            },
        )

        assert output_obj.output_path == fsjoin(tmpdir, "test.json")

        # Check its existence after dumping the output
        output_obj.dump(1.0)
        assert output_obj.exists

        # Check the load value
        assert output_obj.load() == {
            "result": decimal.Decimal(1.0),
            "success": True,
        }
