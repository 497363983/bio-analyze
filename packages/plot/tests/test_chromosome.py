import matplotlib

matplotlib.use("Agg")
from pathlib import Path

import pandas as pd
from bio_analyze_plot.plots.chromosome import ChromosomeDistributionPlot
from matplotlib.figure import Figure


def test_chromosome_plot_generation():
    # Mock data
    # ?? 3 ????????????? 10 ? bin
    chroms = ["chr1", "chr2", "chrX"]
    data_list = []

    for chrom in chroms:
        for i in range(10):
            data_list.append(
                {
                    "chrom": chrom,
                    "pos": i * 100000,
                    "counts_pos": i * 10 + 5,  # ??????
                    "counts_neg": i * 8 + 2,
                }
            )

    data = pd.DataFrame(data_list)

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "chromosome_dist.png"

    plotter = ChromosomeDistributionPlot(theme="nature")
    fig = plotter.plot(
        data=data,
        chrom_col="chrom",
        pos_col="pos",
        pos_counts_col="counts_pos",
        neg_counts_col="counts_neg",
        title="Test Chromosome Distribution",
        output=str(output_file),
    )

    assert isinstance(fig, Figure)
    assert output_file.exists()

    # ?????????
    # chr1, chr2, chrX -> ??? 3 ???
    # ???????? twinx???????????? 2 ? axes ??
    # ?? fig.axes ?????? 3 * 2 = 6
    assert len(fig.axes) == 6


def test_chromosome_plot_max_chroms():
    # ?? max_chroms ??
    data_list = []
    # ?? 5 ????
    for i in range(5):
        chrom = f"chr{i+1}"
        data_list.append({"chrom": chrom, "pos": 0, "counts_pos": 10, "counts_neg": 5})
    data = pd.DataFrame(data_list)

    output_dir = Path(__file__).parent / "output"
    output_file = output_dir / "chromosome_dist_limit.png"

    plotter = ChromosomeDistributionPlot()
    # ????? 2 ?
    fig = plotter.plot(data=data, max_chroms=2, output=str(output_file))

    # ???? 2 ?????? twinx ? 2?? 4 ?
    assert len(fig.axes) == 4
    assert output_file.exists()


def test_chromosome_plot_sorting():
    # ?????????
    chroms = ["chr1", "chr10", "chr2"]
    data_list = []
    for chrom in chroms:
        data_list.append({"chrom": chrom, "pos": 0, "counts_pos": 10, "counts_neg": 5})
    data = pd.DataFrame(data_list)

    plotter = ChromosomeDistributionPlot()
    fig = plotter.plot(data=data)

    # ?? Y ?????
    # ?????????? axes ? ylabel ???????????? axes?
    # ?? axes ??? twinx ???????????? fig.axes ?????
    # ???? axes ?????matplotlib ?????????

    # ??????? axes ? ylabel???????
    ylabels = [ax.get_ylabel() for ax in fig.axes if ax.get_ylabel()]

    # ????: chr1, chr2, chr10
    # ???twinx ??? axes ? ylabel ???? chrom
    assert ylabels == ["chr1", "chr2", "chr10"]


def test_chromosome_plot_custom_colors():
    # ???????
    data = pd.DataFrame([{"chrom": "chr1", "pos": 0, "counts_pos": 10, "counts_neg": 5}])

    plotter = ChromosomeDistributionPlot()
    # ???????
    fig = plotter.plot(data=data, color_pos="blue", color_neg="green")

    # ?????????????
    # ???????? PolyCollection ????
    # ??????? legend handles ???
    legend = fig.legends[0]

    # ?????? patches
    patches = legend.get_patches()
    assert len(patches) == 2

    # ???? (matplotlib ????????????????????
    # ?????????????????????
    # ????????????
    assert isinstance(fig, Figure)
