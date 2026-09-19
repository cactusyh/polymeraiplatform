"""Phase 3 polymer-library API tests."""
def _polymer(client,name,canonical,klass="polyether",architecture="homopolymer"):
    response=client.post("/api/v1/polymers",json={"name":name,"canonical_name":canonical,"polymer_class":klass,"architecture":architecture}); assert response.status_code==201; return response.json()
def test_list_search_filters_sort_and_pagination(client):
    peo=_polymer(client,"Poly(ethylene oxide)","polyethylene_oxide")
    ps=_polymer(client,"Polystyrene","polystyrene",klass="polystyrene")
    assert client.get("/api/v1/polymers",params={"q":"oxide"}).json()["items"][0]["id"]==peo["id"]
    assert client.get("/api/v1/polymers",params={"q":"styrene"}).json()["total"]==1
    assert client.get("/api/v1/polymers",params={"polymer_class":"polyether","architecture":"homopolymer"}).json()["total"]==1
    result=client.get("/api/v1/polymers",params={"limit":1,"offset":1,"sort":"name","order":"desc"}); assert result.status_code==200 and result.json()["limit"]==1 and result.json()["total"]==2
    assert client.get("/api/v1/polymers",params={"limit":101}).status_code==422
    assert client.get("/api/v1/polymers",params={"architecture":"bad"}).status_code==422
def test_provenance_property_filters_structure_patch_and_errors(client):
    polymer=_polymer(client,"Polyethylene","polyethylene")
    definition=client.post("/api/v1/property-definitions",json={"key":"density","name":"Density","canonical_unit":"g/cm^3","category":"physical"}).json()
    provenance=client.post("/api/v1/provenance",json={"source_type":"manual","title":"fixture"}); assert provenance.status_code==201; source=provenance.json()
    assert client.get(f"/api/v1/provenance/{source['id']}").status_code==200
    assert client.get("/api/v1/provenance").json()["total"]==1
    structure=client.post(f"/api/v1/polymers/{polymer['id']}/structures",json={"representation_type":"psmiles","representation":"[*]CC[*]"}); assert structure.status_code==201
    record=client.post(f"/api/v1/polymers/{polymer['id']}/properties",json={"property_definition_id":definition["id"],"value":0,"unit":"g/cm^3","provenance_type":"experiment","provenance_id":source["id"]}); assert record.status_code==201 and record.json()["provenance"]["title"]=="fixture"
    assert client.get("/api/v1/polymers",params={"property_key":"density","provenance_type":"experiment"}).json()["total"]==1
    assert client.get(f"/api/v1/polymers/{polymer['id']}/properties",params={"property_key":"density"}).json()["total"]==1
    patch=client.patch(f"/api/v1/polymers/{polymer['id']}",json={"name":"Updated polyethylene"}); assert patch.status_code==200
    assert client.patch(f"/api/v1/polymers/{polymer['id']}",json={}).status_code==422
    assert client.post("/api/v1/polymers",json={"name":"Duplicate","canonical_name":"polyethylene"}).status_code==409
    assert client.get("/api/v1/polymers/00000000-0000-0000-0000-000000000001").status_code==404
    assert client.post(f"/api/v1/polymers/{polymer['id']}/properties",json={"property_definition_id":"00000000-0000-0000-0000-000000000001","value":1,"unit":"K"}).status_code==404
def test_property_definition_listing(client):
    client.post("/api/v1/property-definitions",json={"key":"band_gap","name":"Band gap","canonical_unit":"eV","category":"electronic"})
    response=client.get("/api/v1/property-definitions",params={"q":"band","category":"electronic"}); assert response.status_code==200 and response.json()["total"]==1
