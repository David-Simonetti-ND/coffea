import os
import uproot
import awkward as ak
from coffea import processor
from coffea.processor.test_items import NanoEventsProcessor


if __name__ == "__main__":
    ak.to_parquet(
        uproot.lazy("tests/samples/nano_dy.root:Events"),
        "nano_dy.parquet",
        list_to32=True,
        use_dictionary=False,
        compression="GZIP",
        compression_level=1,
    )

    ak.to_parquet(
        uproot.lazy("tests/samples/nano_dimuon.root:Events"),
        "nano_dimuon.parquet",
        list_to32=True,
        use_dictionary=False,
        compression="GZIP",
        compression_level=1,
    )

    os.makedirs("/mnt/cephfs/nanoevents/ZJets")
    os.makedirs("/mnt/cephfs/nanoevents/Data")
    for i in range(6):
        os.system(
            f"cp nano_dy.parquet /mnt/cephfs/nanoevents/ZJets/nano_dy.{i}.parquet"
        )
        os.system(
            f"cp nano_dimuon.parquet /mnt/cephfs/nanoevents/Data/nano_dimuon.{i}.parquet"
        )

    from dask.distributed import Client, LocalCluster

    cluster = LocalCluster(processes=True, threads_per_worker=1)
    client = Client(cluster)

    executor = processor.DaskExecutor(client=client)

    run = processor.Runner(
        executor=executor,
        ceph_config_path="/tmp/testradosparquetjob/ceph.conf",
        format="parquet",
    )

    hists = run(
        {
            "ZJets": "/mnt/cephfs/nanoevents/ZJets",
            "Data": "/mnt/cephfs/nanoevents/Data",
        },
        "Events",
        processor_instance=NanoEventsProcessor(),
    )

    assert hists["cutflow"]["ZJets_pt"] == 108
    assert hists["cutflow"]["ZJets_mass"] == 36
    assert hists["cutflow"]["Data_pt"] == 504
    assert hists["cutflow"]["Data_mass"] == 396

    # now run again on parquet files in cephfs (without any pushdown)
    executor_args = {"client": client}

    run = processor.Runner(executor=executor, format="parquet")

    hists = run(
        {
            "ZJets": "/mnt/cephfs/nanoevents/ZJets",
            "Data": "/mnt/cephfs/nanoevents/Data",
        },
        "Events",
        processor_instance=NanoEventsProcessor(),
    )

    assert hists["cutflow"]["ZJets_pt"] == 108
    assert hists["cutflow"]["ZJets_mass"] == 36
    assert hists["cutflow"]["Data_pt"] == 504
    assert hists["cutflow"]["Data_mass"] == 396
