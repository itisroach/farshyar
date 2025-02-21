import re


def ParseMessage(message: str):
    pattern = r"(شانه|متر|تخته|تراکم)?\s*([\d\u06F0-\u06F9]+)\s*(شانه|تراکم|متر|تخته)?"

    matches = re.findall(pattern, message)
    print(matches)
    # Normalize results: Combine number with the correct unit
    results = []
    for unit1, num, unit2 in matches:
        unit = unit1 if unit1 else unit2  # Pick the existing unit

        if unit:  # Only add valid matches
            results.append(num + " " + unit)

    print(results)