import json
from py2neo import Graph, Node,Relationship

graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

with open("disease_sample.json", "r") as file:
    data = json.load(file)


disease_node = Node("Disease",
                    name=data["name"],
                    desc=data["desc"],
                    category=data["category"],
                    prevent=data["prevent"],
                    cause=data["cause"],
                    symptom=data["symptom"],
                    yibao_status=data["yibao_status"],
                    get_prob=data["get_prob"],
                    easy_get=data["easy_get"],
                    get_way=data["get_way"],
                    acompany=data["acompany"],
                    cure_department=data["cure_department"],
                    cure_way=data["cure_way"],
                    cure_lasttime=data["cure_lasttime"],
                    cured_prob=data["cured_prob"],
                    common_drug=data["common_drug"],
                    cost_money=data["cost_money"],
                    check=data["check"],
                    recommand_eat=data["recommand_eat"],
                    recommand_drug=data["recommand_drug"],
                    drug_detail=data["drug_detail"]
                    )


for food in data["do_eat"]:
    food_node = Node("Food", name=food)
    graph.create(food_node)
    graph.create(Relationship(disease_node, "DO_EAT", food_node))
