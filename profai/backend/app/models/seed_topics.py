import json
from .db import Topic, get_session

CANONICAL_OUTLINE = {
  "sections": [
    {"id":"sup","title":"Supervised Learning","goals":["labels","loss","generalization"]},
    {"id":"unsup","title":"Unsupervised Learning","goals":["clustering","dimensionality"]},
    {"id":"rl","title":"Reinforcement Learning","goals":["agent","policy","reward"]},
    {"id":"gen","title":"Generative Models","goals":["density","sampling","diffusion"]}
  ]
}

def seed():
    with get_session() as s:
        if not s.exec("SELECT 1 FROM topic LIMIT 1").first():
            s.add(Topic(slug="ai-model-types", title="Different Types of AI Models", canonical_outline=json.dumps(CANONICAL_OUTLINE)))
            s.commit()