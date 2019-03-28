from typing import Any, Dict, List

from chaosplt_grpc import remote_channel
from chaosplt_grpc.experiment.client import get_experiments

from ..model import Experiment

__all__ = ["ExperimentService"]


class ExperimentService:
    def __init__(self, config: Dict[str, Any]):
        self.exp_addr = config["grpc"]["experiment"]["addr"]

    def release(self):
        pass

    def get_experiments(self, experiment_ids: List[str]) -> List[Experiment]:
        with remote_channel(self.exp_addr) as channel:
            experiments = get_experiments(
                channel, experiment_ids, with_payload=False)
            result = []
            for experiment in experiments:
                result.append(
                    Experiment(
                        id=experiment.id,
                        user_id=experiment.user_id,
                        org_id=experiment.org_id,
                        workspace_id=experiment.workspace_id,
                        created_date=experiment.created_on,
                        updated_date=experiment.updated_on,
                        payload=experiment.payload))
            return result
