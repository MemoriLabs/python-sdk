r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       memorilabs.ai
"""


class Conversation:
    def __init__(self):
        self.summary = None

    def configure_from_advanced_augmentation(self, json_):
        conversation = json_.get("conversation", None)
        if conversation is None:
            return self

        self.summary = conversation.get("summary", None)

        return self


class Entity:
    def __init__(self):
        self.facts = []
        self.semantic_triples = []

    def configure_from_advanced_augmentation(self, json_):
        entity = json_.get("entity", None)
        if entity is None:
            return self

        facts = entity.get("facts", [])
        for fact in facts:
            self.facts.append(fact)

        semantic_triples = entity.get("semantic_triples", [])
        for entry in semantic_triples:
            subject = entry.get("subject", None)
            predicate = entry.get("predicate", None)
            object_ = entry.get("object", None)

            if subject is not None and predicate is not None and object_ is not None:
                subject_name = subject.get("name", None)
                subject_type = subject.get("type", None)
                if subject_name is not None and subject_type is not None:
                    object_name = object_.get("name", None)
                    object_type = object_.get("type", None)
                    if object_name is not None and object_type is not None:
                        semantic_triple = SemanticTriple()
                        semantic_triple.subject_name = subject_name
                        semantic_triple.subject_type = subject_type.lower()
                        semantic_triple.predicate = predicate
                        semantic_triple.object_name = object_name
                        semantic_triple.object_type = object_type.lower()

                        self.semantic_triples.append(semantic_triple)

        return self


class Memories:
    def __init__(self):
        self.conversation = None
        self.entity = None
        self.process = None

    def configure_from_advanced_augmentation(self, json_):
        self.conversation = Conversation().configure_from_advanced_augmentation(json_)
        self.entity = Entity().configure_from_advanced_augmentation(json_)
        self.process = Process().configure_from_advanced_augmentation(json_)
        return self


class Process:
    def __init__(self):
        self.attributes = []

    def configure_from_advanced_augmentation(self, json_):
        process = json_.get("process", None)
        if process is None:
            return self

        attributes = process.get("attributes", [])
        for attribute in attributes:
            self.attributes.append(attribute)

        return self


class SemanticTriple:
    def __init__(self):
        self.subject_name = None
        self.subject_type = None
        self.predicate = None
        self.object_name = None
        self.object_type = None
