# rAdvisor Analysis Notebook

This document describes instructions to use the Jupyter Notebook stored at `analysis/notebooks/RadvisorLogAnalysis.ipynb`, relative to the root of this repository.

## ✅ Prerequisites

To run this notebook, you should already have log files that were created over the course of running an experiment
(or you can use a sample log file),
which should be in an archive named `radvisor.tar.gz`.

Additionally, Python **version 3.9 or above** should be installed on your computer,
which will be used to set up a virtual environment in the next step.
To check the version you already have installed, run `python --version` or `python3 --version`:

```sh
$ python --version
Python 3.9.5
```

## ⚙️ Setting up Jupyter in a virtual environment

> This section was based on [this tutorial](https://janakiev.com/blog/jupyter-virtual-envs/).
> If you have any problems running these steps, it might be useful since it contains a bit more info.

Run all of the commands in this section **from within the `analysis/notebooks` folder**:

First, run the following command to create the virtual environment:

```sh
python -m venv .env
```

Then, activate the virtual environment in the current shell:

```sh
source .env/bin/activate
```

Next, in the same terminal, install all requirements that the notebook needs,
as well as `jupyter` and `notebook`:

```sh
pip install -r requirements.txt
pip install jupyter notebook
```

Afterwards, configure Jupyter to use the python3 binary in the virtual environment:

```sh
python -m ipykernel install --user --name=radvisor-analysis-notebooks-kernel
```

Now, it should be ready to use. Start the Jupyter notebook server by running:

```sh
jupyter notebook
```

Once it is open in your browser and you have navigated to the `RadvisorLogAnalysis.ipynb` file,
you might need to switch kernels to point to the one in the virtual environment.
Simply go to Kernel > Change kernel and select "radvisor-analysis-notebooks-kernel" from the list:

![change kernel](./img/change_kernel.png)

## 👩‍💻 Using the notebook to analyze experiment data

Once you have the notebook open in Jupyter, you're ready to start analyzing rAdvisor experiment data.
It runs on a **single container's utilization data** at a time.
To provide it with the log file to parse, look at the "Notebook inputs" section:
specifically, the following variables:

- `EXPERIMENT_DIRNAME`, which should be set to point to the experiment path (sub-directory in `../data`)
- `NODE_NAME`, which should be set to point to hostname that the container was running on (sub-directory in `../data/{experiment_dirname}/logs`)
- `CONTAINER_ID`, which should be a prefix of or the full Docker container ID (which will be the first part before the underscore in the filenames inside `../data/{experiment_dirname}/logs/{node_name}/radvisor.tar.gz`)

Once these have been set to point to the desired log file, click Cell > Run All in the menu to run the entire notebook:

![run all](./img/run_all.png)

## 📊 Info about each graph and its inputs

### Point-in-time / line graphs

Each of these graphs shows point-in-time data for either CPU utilization, memory usage, or block I/O.
They all have two inputs in common:

- `WINDOW_SIZE_MS` - the size of the window to use to aggregate point-in-time samples together in order to create fewer data points.
  By default, it is `1_000`, which groups all data points into 1-second-wide windows
  (for example, if using the default 50 ms collection interval with rAdvisor, this aggregates 20 data points into a single one).
- `WINDOW_AGGREGATION_FUNCTION` - the function actually used to perform the aggregation.
  It's default value depends on the specific graph, and it accepts any function or function name
  that can be passed to [`pandas.aggregate`](https://pandas.pydata.org/docs/reference/api/pandas.Series.aggregate.html).

#### CPU Point-in-time / line graph

This graph plots the CPU utilization of the container's workload over the course of the experiment.

![cpu point-in-time](./img/radvisor_cpu_pit.png)

#### Memory Point-in-time / line graph

This graph plots the memory usage of the container's workload over the course of the experiment.
This value comes from the `memory.current` value
from the [Linux cgroup v2 memory controller](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html#memory-interface-files),
and is a summary of how much memory a container is "using."

![memory point-in-time](./img/radvisor_mem_pit.png)

#### I/O (Read, Write) Point-in-time / line graph

The two IO graphs plot both Read and Write block (disk) I/O done by the container's workload over the course of the experiment.
Note that reads and writes that only hit the OS's page cache won't appear here, since those happen entirely in-memory.

![i/o point-in-time](./img/radvisor_io_pit.png)

### Histograms

Each of these graphs shows the distribution of raw data points
(except in the case of CPU, which still aggregates per-core data points to a single time-series)
for either CPU utilization, memory usage, or block I/O.

Each graph has a single input, in the format of `{GRAPH}_NUM_BINS`, which controls how many Histogram bins the graph should include
(letting matplotlib automatically size the width of each bin accordingly).

#### CPU Histogram

This graph shows the distribution of CPU usage samples over the course of the experiment.

![cpu histogram](./img/radvisor_cpu_hist.png)

#### Memory Histogram

This graph shows the distribution of memory usage samples over the course of the experiment.

![memory histogram](./img/radvisor_mem_hist.png)

#### I/O (Read, Write) Histograms

The two IO graphs plot the distribution of Read and Write block (disk) I/O done over the course of the experiment.
Each point is taken from the raw read/write data-series, which contain how much data was read from/written to disk in the sampling interval.

![i/o histogram](./img/radvisor_io_hist.png)
