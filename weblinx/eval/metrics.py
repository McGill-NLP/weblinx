import abc
import urllib.parse

import sacrebleu

from ..processing.intent import Intent


class Metric(abc.ABC):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    @abc.abstractmethod
    def score(self, pred, ref, **kwargs):
        raise NotImplementedError

    @abc.abstractclassmethod
    def is_applicable(self, pred, ref):
        """
        This method checks if the metric is applicable to the given prediction and reference.
        If the metric is not applicable, it will return False and the score should be ignored.
        """
        raise NotImplementedError


class LexicalMetric(Metric):
    def is_applicable(self, pred, ref):
        return pred["intent"] == ref["intent"] and pred["intent"] in Intent.get_text_intents()

    def get_texts(self, pred, ref):
        if pred["intent"] == Intent.TEXT_INPUT:
            pred_text = pred["args"].get("text")
            ref_text = ref["args"].get("text")
        elif pred["intent"] == Intent.SAY:
            pred_text = pred["args"].get("utterance")
            ref_text = ref["args"].get("utterance")
        elif pred["intent"] == Intent.LOAD:
            pred_text = pred["args"].get("url")
            ref_text = ref["args"].get("url")
        elif pred["intent"] == Intent.CHANGE:
            pred_text = pred["args"].get("value")
            ref_text = ref["args"].get("value")

        return pred_text, ref_text


class ElementMetric(Metric):
    def is_applicable(self, pred, ref):
        return pred["intent"] == ref["intent"] and pred["intent"] in Intent.get_element_intents()


class IntentMatchMetric(Metric):
    def __init__(self, args={}):
        super().__init__(name="intent-match", args=args)

    def score(self, pred, ref, **kwargs):
        if pred["intent"] != ref["intent"]:
            return 0

        return 1

    def is_applicable(self, pred, ref):
        return True


class ChrFMetric(LexicalMetric):
    def __init__(self, args={}):
        super().__init__(name="chrf", args=args)

    def score(self, pred, ref, **kwargs):
        pred_text, ref_text = self.get_texts(pred, ref)

        if type(pred_text) is not str or type(ref_text) is not str:
            return 0

        score = sacrebleu.sentence_chrf(hypothesis=pred_text, references=[ref_text]).score

        return score / 100


class IOUMetric(ElementMetric):
    def __init__(self, args={}):
        super().__init__(name="iou", args=args)

    def score(self, pred, ref, **kwargs):
        """
        Compute the intersection over union (IOU) of the bounding boxes of the two elements.
        """
        if not pred.get("element") or not ref.get("element"):
            return 0

        bbox_pred = pred["element"].get("bbox")
        bbox_ref = ref["element"].get("bbox")

        if not bbox_pred or not bbox_ref:
            return 0
        
        # To compute the intersection, we need to find the maximum of the left and 
        # minimum of the right
        max_left = max(bbox_pred["left"], bbox_ref["left"])
        min_right = min(bbox_pred["right"], bbox_ref["right"])
        
        # Since bottom value is greater than top value, we need to find the minimum 
        # of the top and maximum of the bottom
        
        max_top = max(bbox_pred["top"], bbox_ref["top"])
        min_bottom = min(bbox_pred["bottom"], bbox_ref["bottom"])
        
        # Compute the intersection area
        intersection_area = max(0, min_right - max_left) * max(0, min_bottom - max_top)
        
        # Compute the union area
        pred_area = (bbox_pred["right"] - bbox_pred["left"]) * (bbox_pred["bottom"] - bbox_pred["top"])
        ref_area = (bbox_ref["right"] - bbox_ref["left"]) * (bbox_ref["bottom"] - bbox_ref["top"])
        union_area = pred_area + ref_area - intersection_area
        
        # Compute the IOU
        iou = intersection_area / union_area
        
        return iou


class URLFMetric(LexicalMetric):
    def __init__(self, args={}):
        super().__init__(name="urlf", args=args)

    def score(self, pred, ref, beta=1, **kwargs):
        pred_text, ref_text = self.get_texts(pred, ref)

        if not pred_text or not ref_text:
            return 0

        try:
            pred_url = urllib.parse.urlparse(pred_text)
            ref_url = urllib.parse.urlparse(ref_text)
        except ValueError:
            return 0

        pred_path = [pred_url.netloc.lstrip("www.")]
        if pred_url.path.strip("/"):
            pred_path += pred_url.path.strip("/").split("/")

        ref_path = [ref_url.netloc.lstrip("www.")]
        if ref_url.path.strip("/"):
            ref_path += ref_url.path.strip("/").split("/")

        # first, compute the recall (tokenR)
        pred_set = set(pred_path)
        ref_set = set(ref_path)
        
        match = pred_set.intersection(ref_set)
        if len(match) == 0:
            return 0
        
        recall = len(match) / len(ref_set)
        precision = len(match) / len(pred_set)
        
        f1 = (1 + beta**2) * (recall * precision) / ((beta**2 * precision) + recall)
        
        return f1
    
    def is_applicable(self, pred, ref):
        return pred["intent"] == ref["intent"] and pred["intent"] == Intent.LOAD


class ExactMatchMetric(Metric):
    def __init__(self, args={}):
        super().__init__(name="exact-match", args=args)

    def score(self, pred, ref, uid_key="data-webtasks-id", **kwargs):
        if pred["intent"] != ref["intent"]:
            return 0

        # check equality of elements
        if pred["intent"] in Intent.get_element_intents():
            if not pred.get("element") or not ref.get("element"):
                return 0

            pred_id = pred["element"]["attributes"].get(uid_key)
            ref_id = ref["element"]["attributes"].get(uid_key)

            if pred_id is None or pred_id != ref_id:
                return 0

        if pred["intent"] == Intent.SAY and pred["args"].get("utterance") != ref["args"].get("utterance"):
            return 0

        if pred["intent"] == Intent.TEXT_INPUT and pred["args"].get("text") != ref["args"].get("text"):
            return 0

        if pred["intent"] == Intent.CHANGE and pred["args"].get("value") != ref["args"].get("value"):
            return 0

        if pred["intent"] == Intent.LOAD and pred["args"].get("url") != ref["args"].get("url"):
            return 0

        if pred["intent"] == Intent.SCROLL and (
            pred["args"].get("x") != ref["args"].get("x") or pred["args"].get("y") != ref["args"].get("y")
        ):
            return 0

        return 1

    def is_applicable(self, pred, ref):
        return True
