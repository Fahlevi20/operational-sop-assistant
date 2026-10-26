"""Opt-in Ragas judging of actual saved runs, not synthetic successes."""

import argparse
import asyncio
import json
import os
from pathlib import Path


def prepare_samples(rows):
    """Map real runs and human-authored references to Ragas inputs."""
    samples = []
    for row in rows:
        result = row["result"]
        response = "\n".join(s["text"] for s in result["statements"])
        if result.get("message"):
            response = (response + "\n" + result["message"]).strip()
        samples.append(
            {
                "id": row["case"]["id"],
                "status": result["status"],
                "expected_status": row["case"]["expected_status"],
                "user_input": result["question"],
                "response": response,
                "reference": row["case"]["reference"],
                "retrieved_contexts": [e["text"] for e in result["evidence"]],
            }
        )
    return samples


async def judge(samples, output):
    """Score faithfulness for answered cases; abstention is evaluated separately."""
    # Avoid optional imports and telemetry during ordinary CLI and offline tests.
    os.environ["RAGAS_DO_NOT_TRACK"] = "true"
    from openai import AsyncOpenAI  # pylint: disable=import-outside-toplevel
    from ragas.llms import llm_factory  # pylint: disable=import-outside-toplevel
    from ragas.metrics.collections import Faithfulness  # pylint: disable=import-outside-toplevel

    client = AsyncOpenAI(timeout=60, max_retries=2)
    llm = llm_factory(os.getenv("OPENAI_JUDGE_MODEL", "gpt-4.1-mini"), client=client)
    metric = Faithfulness(llm=llm)
    scores = []
    for sample in samples:
        row = {"id": sample["id"], "status_matches": sample["status"] == sample["expected_status"]}
        if sample["status"] == "answered":
            result = await metric.ascore(
                user_input=sample["user_input"],
                response=sample["response"],
                retrieved_contexts=sample["retrieved_contexts"],
            )
            row["faithfulness"] = result.value
        else:
            row["faithfulness"] = None
            row["note"] = "Abstention/clarification: manually review against reference."
        scores.append(row)
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(json.dumps({"scores": scores}, indent=2), encoding="utf-8")
    await client.close()


def main():
    """Additional paid judge calls require this explicit command."""
    from dotenv import load_dotenv  # pylint: disable=import-outside-toplevel

    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/evaluation.json")
    parser.add_argument("--output", default="data/ragas.json")
    args = parser.parse_args()
    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))["results"]
    asyncio.run(judge(prepare_samples(rows), args.output))


if __name__ == "__main__":
    main()
