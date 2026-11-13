from .models import AXES, AssessmentBatch, Claim, ClaimAssessment


class DemoSearch:
    calls = 0

    def search(self, query):
        self.calls += 1
        name = next(name for name in ("Notion", "Asana", "monday.com") if name in query)
        axis = next(axis for axis in AXES if query.endswith(axis))
        domain = query.split()[0].removeprefix("site:")
        return [{"url": f"https://{domain}/__synthetic__/{name}/{axis}", "title": f"SYNTHETIC {name} {axis}"}]

    def fetch(self, url):
        name, axis = url.split("/")[-2:]
        return f"SYNTHETIC FIXTURE: {name} {axis} example for pipeline testing. This is not a factual company claim."


class DemoModel:
    def analyze(self, company, criterion, evidence, brief=""):
        return [Claim(company=company, criterion=criterion, text=evidence[0].text,
                      evidence_ids=[evidence[0].id], quote=evidence[0].text)]

    def assess(self, records, evidence, brief=""):
        return AssessmentBatch(assessments=[ClaimAssessment(record=item['record'], verdict='supported',
            reason='Synthetic fixture assessment; not a real quality judgment') for item in records])
