import json
from collections import defaultdict
from pathlib import Path


def prettify_test_name(name: str) -> str:
    name = name.replace("test_should_", "")
    name = name.replace("test_", "")
    name = name.replace("_", " ")
    return name[:1].upper() + name[1:] if name else name


def detect_feature(nodeid: str) -> str:
    if "features/auth_warga" in nodeid or "features\\auth_warga" in nodeid:
        return "Auth Warga"
    if "features/layanan_administrasi" in nodeid or "features\\layanan_administrasi" in nodeid:
        return "Layanan Administrasi"
    if "features/pengaduan_warga" in nodeid or "features\\pengaduan_warga" in nodeid:
        return "Pengaduan Warga"
    return "Lainnya"


def main():
    report_path = Path("report.json")
    if not report_path.exists():
        raise FileNotFoundError("File report.json tidak ditemukan. Jalankan pytest dengan --json-report terlebih dahulu.")

    with report_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    summary = data.get("summary", {})
    tests = data.get("tests", [])

    passed_tests = []
    feature_use_cases = defaultdict(list)
    feature_test_list = defaultdict(list)

    for test in tests:
        if test.get("outcome") != "passed":
            continue

        nodeid = test.get("nodeid", "")
        parts = nodeid.split("::")
        test_func = parts[-1] if parts else nodeid
        feature = detect_feature(nodeid)
        use_case = prettify_test_name(test_func)

        passed_tests.append(nodeid)
        feature_test_list[feature].append(nodeid)
        feature_use_cases[feature].append(use_case)

    lines = []
    lines.append("# Ringkasan Hasil Unit Test")
    lines.append("")
    lines.append("## Ringkasan Umum")
    lines.append("")
    lines.append(f"- Total test dijalankan: **{summary.get('total', 0)}**")
    lines.append(f"- Total test berhasil: **{summary.get('passed', 0)}**")
    lines.append(f"- Total test gagal: **{summary.get('failed', 0)}**")
    lines.append(f"- Total test error: **{summary.get('error', 0)}**")
    lines.append(f"- Total test skipped: **{summary.get('skipped', 0)}**")
    lines.append("")

    lines.append("## Daftar Test yang Berhasil")
    lines.append("")

    for feature, tests_in_feature in feature_test_list.items():
        lines.append(f"### {feature}")
        lines.append("")
        for test_name in tests_in_feature:
            lines.append(f"- `{test_name}`")
        lines.append("")

    lines.append("## Use Case yang Diuji")
    lines.append("")

    for feature, use_cases in feature_use_cases.items():
        lines.append(f"### {feature}")
        lines.append("")
        seen = set()
        for use_case in use_cases:
            if use_case not in seen:
                lines.append(f"- {use_case}")
                seen.add(use_case)
        lines.append("")

    output_path = Path("test_summary.md")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Berhasil membuat {output_path}")


if __name__ == "__main__":
    main()