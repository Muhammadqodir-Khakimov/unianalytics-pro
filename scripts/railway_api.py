"""Railway GraphQL API helper with custom DNS (local DNS bypass).

Local DNS dropping railway.app queries, so we resolve via 8.8.8.8 and pass
the IP to httpx with proper SNI/Host header.
"""
from __future__ import annotations

import json
import os
import sys

import dns.resolver
import httpx


def _resolve(host: str) -> str:
    r = dns.resolver.Resolver()
    r.nameservers = ["8.8.8.8", "1.1.1.1"]
    return str(r.resolve(host, "A")[0])


HOST = "backboard.railway.app"
IP = _resolve(HOST)
URL = f"https://{IP}/graphql/v2"
TOKEN = os.environ["RAILWAY_API_TOKEN"]

_client = httpx.Client(
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    },
    timeout=60,
)


def gql(query: str, variables: dict | None = None) -> dict:
    payload = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    r = _client.post(
        URL,
        headers={"Host": HOST},
        content=json.dumps(payload),
        extensions={"sni_hostname": HOST},
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(json.dumps(data["errors"], indent=2))
    return data["data"]


# ---------- Convenience helpers ----------

PROJECT_ID = "a4e35fe2-62f0-4bd4-af50-2ac696da98f6"
ENV_ID     = "869c3506-ddae-49e6-b87a-87cb10b9e91b"


def list_services() -> list[dict]:
    d = gql(
        "query($id:String!){project(id:$id){services{edges{node{id name}}}}}",
        {"id": PROJECT_ID},
    )
    return [e["node"] for e in d["project"]["services"]["edges"]]


def get_service_by_name(name: str) -> dict | None:
    for s in list_services():
        if s["name"] == name:
            return s
    return None


def create_image_service(name: str, image: str) -> dict:
    d = gql(
        "mutation($input:ServiceCreateInput!){serviceCreate(input:$input){id name}}",
        {"input": {"projectId": PROJECT_ID, "name": name, "source": {"image": image}}},
    )
    return d["serviceCreate"]


def create_repo_service(name: str, repo: str, branch: str = "main") -> dict:
    d = gql(
        "mutation($input:ServiceCreateInput!){serviceCreate(input:$input){id name}}",
        {"input": {"projectId": PROJECT_ID, "name": name, "source": {"repo": repo}, "branch": branch}},
    )
    return d["serviceCreate"]


def set_var(service_id: str, name: str, value: str) -> None:
    gql(
        "mutation($input:VariableUpsertInput!){variableUpsert(input:$input)}",
        {"input": {"projectId": PROJECT_ID, "environmentId": ENV_ID,
                   "serviceId": service_id, "name": name, "value": value}},
    )


def get_vars(service_id: str) -> dict:
    return gql(
        "query($p:String!,$e:String!,$s:String!){variables(projectId:$p,environmentId:$e,serviceId:$s)}",
        {"p": PROJECT_ID, "e": ENV_ID, "s": service_id},
    )["variables"]


def get_service_full(service_id: str) -> dict:
    return gql(
        "query($id:String!){service(id:$id){id name serviceInstances{edges{node{source{image repo}domains{serviceDomains{domain}}}}}}}",
        {"id": service_id},
    )["service"]


def redeploy(service_id: str, env_id: str = ENV_ID) -> dict:
    return gql(
        "mutation($s:String!,$e:String!){serviceInstanceRedeploy(serviceId:$s,environmentId:$e)}",
        {"s": service_id, "e": env_id},
    )


def deploy_via_trigger(service_id: str) -> dict:
    # Trigger deploy via serviceInstanceDeployV2 (latest deployment)
    return gql(
        "mutation($s:String!,$e:String!){serviceInstanceDeployV2(serviceId:$s,environmentId:$e)}",
        {"s": service_id, "e": ENV_ID},
    )


if __name__ == "__main__":
    # Usage: python -m scripts.railway_api list
    if len(sys.argv) < 2 or sys.argv[1] == "list":
        for s in list_services():
            print(f"  {s['id']}  {s['name']}")
