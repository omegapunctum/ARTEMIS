# Synthetic field notebook beta

Status: contract fixture only. The people, places and events below are fictional and must not be interpreted as historical assertions.

## Alternative arrival date

LOCATOR[beta-arrival]
CLAIM_ASSERTION[claim=claim-arrival-event;sha256=a98bf56adaf2d0187a8df1c131f28c17f52921e40d79dfaffff5b549ab9f9d14]
CLAIM_ASSERTION[claim=claim-arrival-event-1504;sha256=b5e1cc4d6e656d6557d3030f2df7347a409a9cff02b7f6c3b259f6a08f60c619]

This notebook places Mara Vale's arrival at Inland Workshop in approximately 1504, not 1503.
PARTICIPANT_ASSERTION[event=event-workshop-arrival;participant=entity-mara-vale]
EXTENT_ASSERTION[owner=event-workshop-arrival;context=event-workshop-arrival;kind=Event;mode=none;dimension=temporal-alternative-0;sha256=8aad0dcda8bff11d4e55cb027a7807b6549e9ff1ca67bc1121f767a07e5d0329]

## Alternative basin boundary

LOCATOR[beta-region-v2]
CLAIM_ASSERTION[claim=claim-region-v2;sha256=f3665bf24488c68da7ada2896d19feda2590c0eb641361fc3d36efe085d11634]
CLAIM_ASSERTION[claim=claim-region-v2-alternative;sha256=ad9c21978dacac45d1f79f03d9c654eb415d58f7198652b9b2df06d626e46e61]

The alternative reconstruction excludes the eastern inlet from the 1504 boundary.
GEOMETRY_ASSERTION[{"coordinates":[[[9.0,49.0],[11.4,49.0],[11.4,51.0],[9.0,51.0],[9.0,49.0]]],"type":"Polygon"}]
EXTENT_ASSERTION[owner=region-fixture-basin;context=region-geometry-v2-alternative;kind=RegionGeometryVersion;mode=alternative_reconstruction;dimension=temporal;sha256=613c04fd983d11ba2bd8835288fc387897aaf42f831a4544eb99bc8c7a862374]
EXTENT_ASSERTION[owner=region-fixture-basin;context=region-geometry-v2-alternative;kind=RegionGeometryVersion;mode=alternative_reconstruction;dimension=spatial;sha256=37c81472b1ac398e362ff4253b2987ccb9bc8b25cd59ed62066a1d923f32ccb7]

## Distant observation

LOCATOR[beta-global-event]
CLAIM_ASSERTION[claim=claim-global-event;sha256=a7176d033d385f443e77fb74fdd86d550ac07a46164344fe35b5981bd0aeb781]

An observation was logged at Far Observatory on 1504-03-01.
GEOMETRY_ASSERTION[{"coordinates":[100.0,-20.0],"type":"Point"}]
EXTENT_ASSERTION[owner=event-far-observation;context=event-far-observation;kind=Event;mode=none;dimension=temporal;sha256=4a706d59db4f108a88f9fada30fd9bf4458381dff0dfdb694b39b2096c249474]
EXTENT_ASSERTION[owner=event-far-observation;context=event-far-observation;kind=Event;mode=none;dimension=spatial;sha256=91a0199853ad826335838f7701b642af8f15dbf5e3ac86f30ba7743b74844a1a]
EXTENT_ASSERTION[owner=world-slice-fixture-basin-v1;context=world-slice-fixture-basin-v1;kind=WorldSlice;mode=coverage;dimension=spatial;sha256=27e4914e4b65530117435e3b7573124e9aa2342487e2a86ffbeab35791266a15]

## Challenged protocol attribution

LOCATOR[beta-influence-ren]
CLAIM_ASSERTION[claim=claim-influence-ren-council;sha256=c443dce8b5961236348e2de17ee5c77f7109a9dc9003b9d111863278820dbb11]

The council minutes attribute the adopted protocol phrase to earlier guild rules and explicitly dispute that Keeper Ren's proposal determined the wording.
