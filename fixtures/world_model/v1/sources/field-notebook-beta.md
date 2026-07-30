# Synthetic field notebook beta

Status: contract fixture only. The people, places and events below are fictional and must not be interpreted as historical assertions.

## Alternative arrival date

LOCATOR[beta-arrival]

This notebook places Mara Vale's arrival at Inland Workshop in approximately 1504, not 1503.
PARTICIPANT_ASSERTION[event=event-workshop-arrival;participant=entity-mara-vale]
EXTENT_ASSERTION[owner=event-workshop-arrival;context=event-workshop-arrival;kind=Event;mode=none;dimension=temporal-alternative-0;sha256=8aad0dcda8bff11d4e55cb027a7807b6549e9ff1ca67bc1121f767a07e5d0329]

## Alternative basin boundary

LOCATOR[beta-region-v2]

The alternative reconstruction excludes the eastern inlet from the 1504 boundary.
GEOMETRY_ASSERTION[{"coordinates":[[[9.0,49.0],[11.4,49.0],[11.4,51.0],[9.0,51.0],[9.0,49.0]]],"type":"Polygon"}]
EXTENT_ASSERTION[owner=region-fixture-basin;context=region-geometry-v2-alternative;kind=RegionGeometryVersion;mode=alternative_reconstruction;dimension=temporal;sha256=613c04fd983d11ba2bd8835288fc387897aaf42f831a4544eb99bc8c7a862374]
EXTENT_ASSERTION[owner=region-fixture-basin;context=region-geometry-v2-alternative;kind=RegionGeometryVersion;mode=alternative_reconstruction;dimension=spatial;sha256=37c81472b1ac398e362ff4253b2987ccb9bc8b25cd59ed62066a1d923f32ccb7]

## Distant observation

LOCATOR[beta-global-event]

An observation was logged at Far Observatory on 1504-03-01.
GEOMETRY_ASSERTION[{"coordinates":[100.0,-20.0],"type":"Point"}]
EXTENT_ASSERTION[owner=event-far-observation;context=event-far-observation;kind=Event;mode=none;dimension=temporal;sha256=4a706d59db4f108a88f9fada30fd9bf4458381dff0dfdb694b39b2096c249474]
EXTENT_ASSERTION[owner=event-far-observation;context=event-far-observation;kind=Event;mode=none;dimension=spatial;sha256=91a0199853ad826335838f7701b642af8f15dbf5e3ac86f30ba7743b74844a1a]

## Challenged protocol attribution

LOCATOR[beta-influence-ren]

The council minutes attribute the adopted protocol phrase to earlier guild rules and explicitly dispute that Keeper Ren's proposal determined the wording.
