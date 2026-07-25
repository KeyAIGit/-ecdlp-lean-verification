def validate(request, artifacts):
    records = artifacts["external-solver-calibration-record"]
    if len(records) != 1:
        return "inconclusive"
    record = records[0]
    if record["instance"] != request["instance"]:
        return "inapplicable"
    if record["left_observation"] == record["right_observation"]:
        return "supported"
    return "falsified"
