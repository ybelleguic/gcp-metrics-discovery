import argparse
import os
import google.auth
from google.api import metric_pb2
from google.api_core.client_options import ClientOptions
from google.cloud import monitoring_v3


def resolve_universe_domain(
    cli_universe: str | None,
    credentials: google.auth.credentials.Credentials,
) -> str:
    """Resolve universe_domain: CLI > env var > ADC > GCP default."""
    if cli_universe:
        return cli_universe

    env_universe = os.getenv("GOOGLE_CLOUD_UNIVERSE_DOMAIN")
    if env_universe:
        return env_universe

    cred_universe = getattr(credentials, "universe_domain", None)
    if cred_universe:
        return cred_universe

    return "googleapis.com"


def list_metrics(
    project_id: str | None,
    prefix: str | None = None,
    active_only: bool = True,
    cli_universe: str | None = None,
) -> None:
    credentials, detected_project = google.auth.default()
    target_project = project_id or detected_project
    if not target_project:
        raise ValueError(
            "Project not found. Pass -p/--project or set GOOGLE_CLOUD_PROJECT."
        )

    universe_domain = resolve_universe_domain(cli_universe, credentials)

    # Align the domain on credentials if a legacy user ADC does not include the field
    if (
        getattr(credentials, "universe_domain", None) != universe_domain
        and hasattr(credentials, "_universe_domain")
    ):
        credentials._universe_domain = universe_domain

    client_options = ClientOptions(universe_domain=universe_domain)
    client = monitoring_v3.MetricServiceClient(
        credentials=credentials,
        client_options=client_options,
    )

    filter_expr = f'metric.type = starts_with("{prefix}")' if prefix else ""
    request = monitoring_v3.ListMetricDescriptorsRequest(
        name=f"projects/{target_project}",
        filter=filter_expr,
        active_only=active_only,
    )

    descriptors = list(client.list_metric_descriptors(request=request))
    print(f"Universe: {universe_domain} | Project: {target_project}")
    print(f"Metrics found ({len(descriptors)}):\n")

    for desc in descriptors:
        labels = ", ".join(label.key for label in desc.labels) or "none"
        try:
            metric_kind = metric_pb2.MetricDescriptor.MetricKind.Name(desc.metric_kind)
        except ValueError:
            metric_kind = str(desc.metric_kind)
        try:
            value_type = metric_pb2.MetricDescriptor.ValueType.Name(desc.value_type)
        except ValueError:
            value_type = str(desc.value_type)
        print(f"- {desc.type}")
        print(f"  Kind: {metric_kind} | Type: {value_type} | Unit: {desc.unit or '-'}")
        print(f"  Labels: [{labels}]")
        if desc.description:
            print(f"  Desc: {desc.description}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover GCP / S3NS / GCD Cloud Monitoring metrics"
    )
    parser.add_argument(
        "-p", "--project",
        default=os.getenv("GOOGLE_CLOUD_PROJECT"),
        help="Project ID (automatically inferred from ADC if omitted)",
    )
    parser.add_argument(
        "-u", "--universe-domain",
        default=None,
        help='Universe domain (e.g. "s3nsapis.fr"). Inferred from ADC or GOOGLE_CLOUD_UNIVERSE_DOMAIN if omitted',
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help='Filter by metric type prefix (e.g. "compute.googleapis.com/")',
    )
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help="Include the full theoretical catalog even without recent data",
    )
    args = parser.parse_args()

    list_metrics(
        project_id=args.project,
        prefix=args.prefix,
        active_only=not args.include_inactive,
        cli_universe=args.universe_domain,
    )


if __name__ == "__main__":
    main()
