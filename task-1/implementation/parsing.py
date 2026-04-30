import json
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List

class TestStatus(Enum):
    PASSED = 1
    FAILED = 2
    SKIPPED = 3
    ERROR = 4

@dataclass
class TestResult:
    name: str
    status: TestStatus

def parse_junit_xml(xml_file: Path) -> List[TestResult]:
    results = []
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    for testcase in root.findall(".//testcase"):
        name = testcase.get("name")
        classname = testcase.get("classname")
        full_name = f"{classname}.{name}"
        
        status = TestStatus.PASSED
        if testcase.find("failure") is not None:
            status = TestStatus.FAILED
        elif testcase.find("error") is not None:
            status = TestStatus.ERROR
        elif testcase.find("skipped") is not None:
            status = TestStatus.SKIPPED
            
        results.append(TestResult(name=full_name, status=status))
    return results

def main():
    # Gradle puts JUnit XML results in build/test-results/test/
    test_results_dir = Path("build/test-results/test")
    all_results = []

    if test_results_dir.exists():
        for xml_file in test_results_dir.glob("*.xml"):
            all_results.extend(parse_junit_xml(xml_file))

    # Convert Enum to string for JSON serialization
    output_data = [
        {"name": r.name, "status": r.status.name} for r in all_results
    ]

    print(json.dumps(output_data, indent=2))

if __name__ == "__main__":
    main()
