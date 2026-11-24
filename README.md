# Monitoring Metrics Discovery

A Python CLI tool to discover and list Cloud Monitoring metric descriptors across **Google Cloud Platform (GCP)**, **Cloud de Confiance by S3NS**, and **Google Cloud Dedicated (GCD)**.

## What It Does

This tool queries the Cloud Monitoring API (`ListMetricDescriptors`) for a target project and prints a readable summary of matching metrics, including:

- Metric type (e.g., `compute.googleapis.com/instance/cpu/utilization`)
- Metric kind (`GAUGE`, `DELTA`, `CUMULATIVE`, etc.), value type (`DOUBLE`, `INT64`, `DISTRIBUTION`, etc.), and unit
- Available metric labels
- Metric description

It supports sovereign cloud universes out of the box and automatically resolves the target `universe_domain` using the following precedence order:

1. `-u` / `--universe-domain` CLI argument
2. `GOOGLE_CLOUD_UNIVERSE_DOMAIN` environment variable
3. `universe_domain` attribute from Application Default Credentials (ADC)
4. Default fallback: `googleapis.com`

## Prerequisites

- **Python** `>= 3.13`
- **[uv](https://docs.astral.sh/uv/)** (recommended for dependency management)
- **Application Default Credentials (ADC)** configured for your target cloud environment (via `gcloud auth application-default login`, Workforce Identity Federation, or `GOOGLE_APPLICATION_CREDENTIALS`)
- IAM permission `monitoring.metricDescriptors.list` on the target project (for example, the `roles/monitoring.viewer` role)

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd monitoring
   ```

2. Install dependencies with `uv`:

   ```bash
   uv sync
   ```

## Usage

Run the CLI via `uv`:

```bash
uv run main.py [OPTIONS]
```

### CLI Options

| Option | Description | Default |
| --- | --- | --- |
| `-p`, `--project <PROJECT_ID>` | Target project ID. For sovereign clouds, include the universe prefix (e.g., `s3ns:my-project`). | `GOOGLE_CLOUD_PROJECT` env var, then ADC default project |
| `-u`, `--universe-domain <DOMAIN>` | Target universe domain (e.g., `googleapis.com`, `s3nsapis.fr`). | `GOOGLE_CLOUD_UNIVERSE_DOMAIN` env var, then ADC, then `googleapis.com` |
| `--prefix <PREFIX>` | Filter metrics by metric type prefix (e.g., `compute.googleapis.com/`). | None (returns all metrics) |
| `--include-inactive` | Include the full theoretical metric catalog, even metrics with no recent time series data (`active_only=False`). | Disabled (only active metrics are listed) |
| `-h`, `--help` | Show help message and exit. | — |

### Environment Variables

| Variable | Description |
| --- | --- |
| `GOOGLE_CLOUD_PROJECT` | Default project ID used when `-p` / `--project` is omitted. |
| `GOOGLE_CLOUD_UNIVERSE_DOMAIN` | Default universe domain used when `-u` / `--universe-domain` is omitted. |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to a service account key or external account (Workforce/Workload Identity) credential file. |

## Examples

### Public Google Cloud

List active metrics for a GCP project:

```bash
uv run main.py -p my-gcp-project
```

Filter active Compute Engine metrics by prefix:

```bash
uv run main.py -p my-gcp-project --prefix "compute.googleapis.com/"
```

Include inactive metric descriptors:

```bash
uv run main.py -p my-gcp-project --prefix "compute.googleapis.com/" --include-inactive
```

### Cloud de Confiance by S3NS

```bash
uv run main.py -u s3nsapis.fr -p s3ns:my-project
```

### Using Environment Variables

```bash
export GOOGLE_CLOUD_UNIVERSE_DOMAIN="s3nsapis.fr"
export GOOGLE_CLOUD_PROJECT="s3ns:my-project"
uv run main.py --prefix "compute.googleapis.com/"
```

## Example Output

```text
Universe: googleapis.com | Project: my-gcp-project
Metrics found (1):

- compute.googleapis.com/instance/cpu/utilization
  Kind: GAUGE | Type: DOUBLE | Unit: 10^2.%
  Labels: [instance_name]
  Desc: Fractional utilization of allocated CPU on this instance.
```
