import sys
import os.path as osp
import pytest
from coffea import processor
from coffea.nanoevents import schemas

if sys.platform.startswith("win"):
    pytest.skip("skipping tests that only function in linux", allow_module_level=True)


@pytest.mark.parametrize("maxchunks", [None, 1000])
@pytest.mark.parametrize("compression", [None, 0, 2])
@pytest.mark.parametrize(
    "executor", [processor.IterativeExecutor, processor.FuturesExecutor]
)
def test_nanoevents_analysis(executor, compression, maxchunks):
    from coffea.processor.test_items import NanoEventsProcessor

    filelist = {
        "DummyBad": {
            "treename": "Events",
            "files": [osp.abspath("tests/samples/non_existent.root")],
        },
        "ZJets": {
            "treename": "Events",
            "files": [osp.abspath("tests/samples/nano_dy.root")],
            "metadata": {"checkusermeta": True, "someusermeta": "hello"},
        },
        "Data": {
            "treename": "Events",
            "files": [osp.abspath("tests/samples/nano_dimuon.root")],
            "metadata": {"checkusermeta": True, "someusermeta2": "world"},
        },
    }

    executor = executor(compression=compression)
    run = processor.Runner(
        executor=executor,
        skipbadfiles=True,
        schema=processor.NanoAODSchema,
        maxchunks=maxchunks,
    )

    hists = run(filelist, "Events", processor_instance=NanoEventsProcessor())

    assert hists["cutflow"]["ZJets_pt"] == 18
    assert hists["cutflow"]["ZJets_mass"] == 6
    assert hists["cutflow"]["Data_pt"] == 84
    assert hists["cutflow"]["Data_mass"] == 66


@pytest.mark.parametrize("chunksize", [100000, 5])
@pytest.mark.parametrize("schema", [None, schemas.BaseSchema])
@pytest.mark.parametrize(
    "executor", [processor.IterativeExecutor, processor.FuturesExecutor]
)
def test_dataframe_analysis(executor, schema, chunksize):
    from coffea.processor.test_items import NanoTestProcessor

    filelist = {
        "ZJets": [osp.abspath("tests/samples/nano_dy.root")],
        "Data": [osp.abspath("tests/samples/nano_dimuon.root")],
    }

    executor = executor()
    run = processor.Runner(executor=executor, schema=schema, chunksize=chunksize)

    hists = run(filelist, "Events", processor_instance=NanoTestProcessor())

    assert hists["cutflow"]["ZJets_pt"] == 18
    assert hists["cutflow"]["ZJets_mass"] == 6
    assert hists["cutflow"]["Data_pt"] == 84
    assert hists["cutflow"]["Data_mass"] == 66
