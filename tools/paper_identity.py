"""Identify a manuscript from explicit identifiers, never from citations."""
from __future__ import annotations

import re
from collections.abc import Mapping
from urllib.parse import urlsplit, unquote

_ARXIV = re.compile(r"^(?:\d{4}\.\d{4,5}|[a-z][a-z.-]+/\d{7})(?:v\d+)?$", re.I)
_ACL = re.compile(r"^(?:\d{4}\.[a-z0-9][a-z0-9.-]*\.\d+|[A-Z]\d{2}-\d{4,5})$", re.I)


def _values(draft):
    names = ("arxiv_id", "doi", "canonical_id", "paper_url")
    return [str((draft.get(name, "") if isinstance(draft, Mapping) else getattr(draft, name, "")) or "").strip()
            for name in names]


def detectIdentity(draft):
    """Return identity type and ID; both keeps arXiv as legacy canonical ID."""
    arxiv = ""
    acl = ""
    for value in _values(draft):
        if not value:
            continue
        value = re.sub(r"^(?:arxiv:|doi:)", "", value, flags=re.I)
        parts = urlsplit(value)
        if parts.scheme:
            if parts.scheme.lower() not in ("http", "https") or parts.username or parts.password:
                continue
            host = (parts.hostname or "").lower()
            path = unquote(parts.path).strip("/")
            if host in ("arxiv.org", "www.arxiv.org", "export.arxiv.org"):
                if not path.startswith(("abs/", "pdf/")):
                    continue
                candidate = path.split("/", 1)[1].removesuffix(".pdf")
            elif host in ("doi.org", "dx.doi.org"):
                candidate = path
            elif host in ("aclanthology.org", "www.aclanthology.org"):
                candidate = "10.18653/v1/" + path.removesuffix(".pdf")
            else:
                continue
        else:
            candidate = value
        if _ARXIV.fullmatch(candidate):
            arxiv = arxiv or re.sub(r"v\d+$", "", candidate, flags=re.I)
        elif candidate.lower().startswith("10.18653/v1/"):
            suffix = candidate[len("10.18653/v1/"):]
            if _ACL.fullmatch(suffix):
                acl = acl or "10.18653/v1/" + suffix
    kind = "both" if arxiv and acl else "arxiv" if arxiv else "acl_doi" if acl else "none"
    return {"type": kind, "canonicalId": arxiv or acl}


def identityStatus(draft):
    """Identity gate only; ready is not a publication or article-quality receipt.

    Preserve ready for arXiv/both; ready_non_arxiv denotes recognized ACL DOI.
    """
    kind = detectIdentity(draft)["type"]
    if kind == "none":
        return "blocked_non_arxiv"
    if kind == "acl_doi":
        return "ready_non_arxiv"
    return "ready"


def _identity_key_from_doi(doi: str) -> str:
    """Derive a filesystem/Notion-safe key from an ACL DOI.

    10.18653/v1/2026.findings-acl.1001 -> acl-2026-findings-acl-1001
    Only '/', '.' and whitespace are normalized; the rest is preserved so the
    key stays traceable back to the DOI.
    """
    suffix = doi[len("10.18653/v1/"):] if doi.lower().startswith("10.18653/v1/") else doi
    cleaned = re.sub(r"[/.\s]+", "-", suffix).strip("-")
    return f"acl-{cleaned}" if cleaned else ""


def identityKey(draft) -> str:
    """One stable key for dedup, on-disk paths and receipts.

    arxiv -> normalized arxiv_id (version suffix removed)
    acl_doi -> safe slug derived from the DOI
    both -> arxiv wins (backward compatible with the existing arxiv-keyed library)
    none -> empty string (write guard blocks on this)
    """
    identity = detectIdentity(draft)
    kind = identity["type"]
    if kind in ("arxiv", "both"):
        value = draft.get("arxiv_id", "") if isinstance(draft, Mapping) else getattr(draft, "arxiv_id", "")
        value = re.sub(r"^(?:arxiv:)", "", str(value or "").strip(), flags=re.I)
        return re.sub(r"v\d+$", "", value, flags=re.I)
    if kind == "acl_doi":
        return _identity_key_from_doi(identity["canonicalId"])
    return ""


def canWriteSafely(draft) -> bool:
    """The single write precondition: a non-empty, recognized identity key."""
    return bool(identityKey(draft))


def needs_arxiv_for_write(draft) -> bool:
    """Deprecated: legacy arxiv-only guard kept only for old callers/tests.

    New code must use canWriteSafely(); this function still reports True for
    ACL-only papers and is NOT the write gate anymore.
    """
    value = draft.get("arxiv_id", "") if isinstance(draft, Mapping) else getattr(draft, "arxiv_id", "")
    return detectIdentity({"arxiv_id": value})["type"] != "arxiv"
