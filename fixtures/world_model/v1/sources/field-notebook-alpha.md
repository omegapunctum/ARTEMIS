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
EXTENT_ASSERTION[owner=event-north-harbor-charter;context=event-north-harbor-charter;kind=Event;mode=none;dimension=temporal;sha256=d12dd97406d97505eed11906f3510715d2231d6a0a2ea03b7dd30d304687592c]
EXTENT_ASSERTION[owner=event-north-harbor-charter;context=event-north-harbor-charter;kind=Event;mode=none;dimension=spatial;sha256=43055dfc3356f4b515e9a347d037453c7ca2ada941a4884301fb92e20d6dda97]

## Workshop arrival

LOCATOR[alpha-arrival]

The compiler dates Mara Vale's arrival at Inland Workshop to approximately 1503.
PARTICIPANT_ASSERTION[event=event-workshop-arrival;participant=entity-mara-vale]
EXTENT_ASSERTION[owner=event-workshop-arrival;context=event-workshop-arrival;kind=Event;mode=none;dimension=temporal;sha256=38b413198a90773460768d4917e682eef776137e94514ab785e35082969262e8]
EXTENT_ASSERTION[owner=event-workshop-arrival;context=event-workshop-arrival;kind=Event;mode=none;dimension=spatial;sha256=eaa94122c72b16a6a91305a3603f8ab308c30585d449254433c65e06ee2fcb31]

## Administration state

LOCATOR[alpha-administration]

The North Harbor council administered the basin from 1500 through 1508.
EXTENT_ASSERTION[owner=state-north-harbor-administration;context=state-north-harbor-administration;kind=State;mode=none;dimension=temporal;sha256=a74aee96364b0dcff1039c01e7a249fb7c993cf83c797e7867b72045490d5272]
EXTENT_ASSERTION[owner=state-north-harbor-administration;context=state-north-harbor-administration;kind=State;mode=none;dimension=spatial;sha256=f3c1621752fd8360a4efc4058f633a4c686b5175c1ff094b7b0b826f5341f2ca]

## Coastal exchange stages

LOCATOR[alpha-process-north]

Exchange markers were recorded across the Fixture Basin region around North Harbor from 1498 through 1503.
EXTENT_ASSERTION[owner=process-coastal-exchange;context=process-stage-north;kind=ProcessStage;mode=none;dimension=temporal;sha256=bdc3a7a8f72190886324fe2e796be57231a52024735e7fac3e3c70f4737b44b6]
EXTENT_ASSERTION[owner=process-coastal-exchange;context=process-stage-north;kind=ProcessStage;mode=none;dimension=spatial;sha256=7cf250952bf7faad2e635606c7f8ed1b97654eeee95436a201ac10b8606ae039]

LOCATOR[alpha-process-south]

Comparable markers were recorded within the South Coast analytical region around South Port from 1504 through 1510.
EXTENT_ASSERTION[owner=process-coastal-exchange;context=process-stage-south;kind=ProcessStage;mode=none;dimension=temporal;sha256=016c7e8c033f0afa7a214776b1500a232b4881ba785689faee35a8a0fb1dd217]
EXTENT_ASSERTION[owner=process-coastal-exchange;context=process-stage-south;kind=ProcessStage;mode=none;dimension=spatial;sha256=ef81fddc2d67b7912340468602be86c1bcca6048198994bcc6b20b54556ce788]

LOCATOR[alpha-region-south]

For this analytical fixture, the reviewed South Coast region encloses the South Port marker observations from 1504 through 1510.
GEOMETRY_ASSERTION[{"coordinates":[[[19.0,39.0],[22.0,39.0],[22.0,42.0],[19.0,42.0],[19.0,39.0]]],"type":"Polygon"}]
EXTENT_ASSERTION[owner=region-south-coast;context=region-south-coast-v1;kind=RegionGeometryVersion;mode=analytical_model;dimension=temporal;sha256=f8a0b7e18784f33f8e6c3104a0b2eb1885e53422088d08e30aecb02028ffddc7]
EXTENT_ASSERTION[owner=region-south-coast;context=region-south-coast-v1;kind=RegionGeometryVersion;mode=analytical_model;dimension=spatial;sha256=410d9514730a0ed9f23e477af55d34b1efba2e6cf794e32370bcecab0de7b90e]

## Trajectory endpoints

LOCATOR[alpha-trajectory-north]

Mara Vale was recorded at North Harbor from 1499 through 1501.
EXTENT_ASSERTION[owner=trajectory-mara-vale;context=trajectory-segment-north;kind=TrajectorySegment;mode=presence;dimension=temporal;sha256=b6084998268a18b9c069c89b7857130d5a138727bf5396ede7d20d046cf5181e]
EXTENT_ASSERTION[owner=trajectory-mara-vale;context=trajectory-segment-north;kind=TrajectorySegment;mode=presence;dimension=spatial;sha256=f80c291948659cba3c0026e63b2179920a96a4ea4307721b259ab7d1c98e6ba4]

LOCATOR[alpha-trajectory-gap]

The unobserved trajectory gap runs from 1501 through 1504 between the recorded North Harbor and Inland Workshop endpoints; its route is unknown.
EXTENT_ASSERTION[owner=trajectory-mara-vale;context=trajectory-segment-gap;kind=TrajectorySegment;mode=inferred_gap;dimension=temporal;sha256=f852de326c6709dcf51203ca04cec7c947097070b5d07344c1af59fd64cd3755]
EXTENT_ASSERTION[owner=trajectory-mara-vale;context=trajectory-segment-gap;kind=TrajectorySegment;mode=inferred_gap;dimension=spatial;sha256=0b79f0612dcc1ecc64332120696fbf11f6cc56e31e718f84b489801cd2f8ef4a]

LOCATOR[alpha-trajectory-workshop]

Mara Vale was recorded at Inland Workshop from 1504 through 1508.
EXTENT_ASSERTION[owner=state-mara-workshop-presence;context=state-mara-workshop-presence;kind=State;mode=none;dimension=temporal;sha256=9e96d8d52918be21c6a16271a01484237ecb9222209f679af68d43cc9438bb35]
EXTENT_ASSERTION[owner=state-mara-workshop-presence;context=state-mara-workshop-presence;kind=State;mode=none;dimension=spatial;sha256=56a7e92d7e87e31f08879a5f1fb9b89e00ed2ac5f0e5311659f70f65eebd5adf]
EXTENT_ASSERTION[owner=trajectory-mara-vale;context=trajectory-segment-workshop;kind=TrajectorySegment;mode=presence;dimension=temporal;sha256=5cc26bdc59ad4d7e2cf77ed0e1d7fa6db0a1e5a7d1d22ec27b42dcea54d3c3a4]
EXTENT_ASSERTION[owner=trajectory-mara-vale;context=trajectory-segment-workshop;kind=TrajectorySegment;mode=presence;dimension=spatial;sha256=2e4540c6676b955bd1fb15c10d94b3a8f43c2b44cda271311bc5dd82a079bb27]

## Independent workshop presence

LOCATOR[alpha-traveler-workshop]

Traveler Sol was recorded at Inland Workshop during 1505. The notebook records no meeting, exchange or relationship between Traveler Sol and Mara Vale.
EXTENT_ASSERTION[owner=state-traveler-workshop-presence;context=state-traveler-workshop-presence;kind=State;mode=none;dimension=temporal;sha256=e4264d84dfebe005b6385475abaf670274bbc470c266e70c4598f1db2214854b]
EXTENT_ASSERTION[owner=state-traveler-workshop-presence;context=state-traveler-workshop-presence;kind=State;mode=none;dimension=spatial;sha256=02a7dffa092c32c2ee44da88b17524c923bb2716c0458d69baba554d9021aabb]

## Basin boundary versions

LOCATOR[alpha-region-v1]

For the fixture, the reviewed reconstruction uses boundary version A from 1498 through 1503.
GEOMETRY_ASSERTION[{"coordinates":[[[9.0,49.0],[11.0,49.0],[11.0,51.0],[9.0,51.0],[9.0,49.0]]],"type":"Polygon"}]
EXTENT_ASSERTION[owner=region-fixture-basin;context=region-geometry-v1;kind=RegionGeometryVersion;mode=scholarly_reconstruction;dimension=temporal;sha256=cbe37594ea36e26df2658c67626248f4d3c35d692ab3f1a0e779037e5e3d0820]
EXTENT_ASSERTION[owner=region-fixture-basin;context=region-geometry-v1;kind=RegionGeometryVersion;mode=scholarly_reconstruction;dimension=spatial;sha256=15e48c745179e273d94f6b492252a9b142557bc196137c5ce917f8abb04a6cd6]

LOCATOR[alpha-region-v2]

For the fixture, the reviewed reconstruction uses the expanded boundary version B from 1504 through 1510.
GEOMETRY_ASSERTION[{"coordinates":[[[9.0,49.0],[12.0,49.0],[12.0,51.0],[9.0,51.0],[9.0,49.0]]],"type":"Polygon"}]
EXTENT_ASSERTION[owner=region-fixture-basin;context=region-geometry-v2;kind=RegionGeometryVersion;mode=scholarly_reconstruction;dimension=temporal;sha256=b9994974b1c010eea46645d310dd5132ac6d61e3e9a135f342dc68f0a605a980]
EXTENT_ASSERTION[owner=region-fixture-basin;context=region-geometry-v2;kind=RegionGeometryVersion;mode=scholarly_reconstruction;dimension=spatial;sha256=44b5bc2d6410417a4f8c023da66b224f7310b24dfd298b94b7ebae2aa9af88ed]

## Documented encounter

LOCATOR[alpha-encounter]

The register records Mara Vale and Keeper Ren in the same meeting at Inland Workshop on 1504-03-01.
PARTICIPANT_ASSERTION[event=event-documented-workshop-meeting;participant=entity-mara-vale]
PARTICIPANT_ASSERTION[event=event-documented-workshop-meeting;participant=entity-keeper-ren]
RELATION_ASSERTION[{"directionality":"symmetric","mechanism":null,"object_ref":"entity-keeper-ren","predicate":"documented_encounter","relation_ref":"relation-mara-ren-encounter","scope":null,"spatial_extent":{"basis_claim_refs":["claim-documented-encounter"],"kind":"named_place","place_ref":"place-inland-workshop","precision":"fixture_defined"},"subject_ref":"entity-mara-vale","temporal_extent":{"basis_claim_refs":["claim-documented-encounter"],"calendar":"proleptic_gregorian","certainty":"fixture_defined","end":"1504-03-01","kind":"instant","precision":"day","start":"1504-03-01"}}]
EXTENT_ASSERTION[owner=event-documented-workshop-meeting;context=event-documented-workshop-meeting;kind=Event;mode=none;dimension=temporal;sha256=d78bdc5593004596f129d5e4bcbcdc4f183ec417ed6f8587f25dccbb16d4b759]
EXTENT_ASSERTION[owner=event-documented-workshop-meeting;context=event-documented-workshop-meeting;kind=Event;mode=none;dimension=spatial;sha256=d74d8082fcd8b304c7b813958e1382e99dd2807503ffdbab7fbfc7fee680e2e1]

## Contested protocol influence

LOCATOR[alpha-influence-ren]

The register states that during 1504–1505 Keeper Ren proposed the phrase later adopted in the North Harbor council protocol.
RELATION_ASSERTION[{"directionality":"directed","mechanism":"A proposed protocol phrase is asserted to have affected the council text, but the attribution is challenged by a second fixture source.","object_ref":"entity-north-harbor-council","predicate":"influence","relation_ref":"relation-ren-influences-council-protocol","scope":"North Harbor council protocol wording only","spatial_extent":{"basis_claim_refs":["claim-influence-ren-council"],"kind":"named_place","place_ref":"place-north-harbor","precision":"fixture_defined"},"subject_ref":"entity-keeper-ren","temporal_extent":{"basis_claim_refs":["claim-influence-ren-council"],"calendar":"proleptic_gregorian","certainty":"contested","end":"1505","kind":"closed_interval","precision":"year","start":"1504"}}]
