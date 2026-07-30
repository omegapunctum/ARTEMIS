# Synthetic field notebook alpha

Status: contract fixture only. The people, places and events below are fictional and must not be interpreted as historical assertions.

## Identity record

LOCATOR[alpha-identity]

The notebook identifies Mara Vale as the surveyor whose movements are recorded in the remaining entries.

## North Harbor charter

LOCATOR[alpha-charter]

The charter ceremony occurred at North Harbor on 1500-06-15 with Mara Vale participating.
PARTICIPANT_ASSERTION[event=event-north-harbor-charter;participant=entity-mara-vale]
GEOMETRY_ASSERTION[{"coordinates":[10.0,50.0],"type":"Point"}]

## Workshop arrival

LOCATOR[alpha-arrival]

The compiler dates Mara Vale's arrival at Inland Workshop to approximately 1503.
PARTICIPANT_ASSERTION[event=event-workshop-arrival;participant=entity-mara-vale]

## Administration state

LOCATOR[alpha-administration]

The North Harbor council administered the basin from 1500 through 1508.

## Coastal exchange stages

LOCATOR[alpha-process-north]

Exchange markers were recorded across the Fixture Basin region around North Harbor from 1498 through 1503.

LOCATOR[alpha-process-south]

Comparable markers were recorded within the South Coast analytical region around South Port from 1504 through 1510.

LOCATOR[alpha-region-south]

For this analytical fixture, the reviewed South Coast region encloses the South Port marker observations from 1504 through 1510.
GEOMETRY_ASSERTION[{"coordinates":[[[19.0,39.0],[22.0,39.0],[22.0,42.0],[19.0,42.0],[19.0,39.0]]],"type":"Polygon"}]

## Trajectory endpoints

LOCATOR[alpha-trajectory-north]

Mara Vale was recorded at North Harbor from 1499 through 1501.

LOCATOR[alpha-trajectory-gap]

Only the North Harbor and Inland Workshop endpoints are recorded; the route between them is unknown.

LOCATOR[alpha-trajectory-workshop]

Mara Vale was recorded at Inland Workshop from 1504 through 1508.

## Independent workshop presence

LOCATOR[alpha-traveler-workshop]

Traveler Sol was recorded at Inland Workshop during 1505. The notebook records no meeting, exchange or relationship between Traveler Sol and Mara Vale.

## Basin boundary versions

LOCATOR[alpha-region-v1]

For the fixture, the reviewed reconstruction uses boundary version A from 1498 through 1503.
GEOMETRY_ASSERTION[{"coordinates":[[[9.0,49.0],[11.0,49.0],[11.0,51.0],[9.0,51.0],[9.0,49.0]]],"type":"Polygon"}]

LOCATOR[alpha-region-v2]

For the fixture, the reviewed reconstruction uses the expanded boundary version B from 1504 through 1510.
GEOMETRY_ASSERTION[{"coordinates":[[[9.0,49.0],[12.0,49.0],[12.0,51.0],[9.0,51.0],[9.0,49.0]]],"type":"Polygon"}]

## Documented encounter

LOCATOR[alpha-encounter]

The register records Mara Vale and Keeper Ren in the same meeting at Inland Workshop on 1504-03-01.
PARTICIPANT_ASSERTION[event=event-documented-workshop-meeting;participant=entity-mara-vale]
PARTICIPANT_ASSERTION[event=event-documented-workshop-meeting;participant=entity-keeper-ren]
RELATION_ASSERTION[{"directionality":"symmetric","mechanism":null,"object_ref":"entity-keeper-ren","predicate":"documented_encounter","relation_ref":"relation-mara-ren-encounter","scope":null,"spatial_extent":{"basis_claim_refs":["claim-documented-encounter"],"kind":"named_place","place_ref":"place-inland-workshop","precision":"fixture_defined"},"subject_ref":"entity-mara-vale","temporal_extent":{"basis_claim_refs":["claim-documented-encounter"],"calendar":"proleptic_gregorian","certainty":"fixture_defined","end":"1504-03-01","kind":"instant","precision":"day","start":"1504-03-01"}}]

## Contested protocol influence

LOCATOR[alpha-influence-ren]

The register states that during 1504–1505 Keeper Ren proposed the phrase later adopted in the North Harbor council protocol.
RELATION_ASSERTION[{"directionality":"directed","mechanism":"A proposed protocol phrase is asserted to have affected the council text, but the attribution is challenged by a second fixture source.","object_ref":"entity-north-harbor-council","predicate":"influence","relation_ref":"relation-ren-influences-council-protocol","scope":"North Harbor council protocol wording only","spatial_extent":{"basis_claim_refs":["claim-influence-ren-council"],"kind":"named_place","place_ref":"place-north-harbor","precision":"fixture_defined"},"subject_ref":"entity-keeper-ren","temporal_extent":{"basis_claim_refs":["claim-influence-ren-council"],"calendar":"proleptic_gregorian","certainty":"contested","end":"1505","kind":"closed_interval","precision":"year","start":"1504"}}]
