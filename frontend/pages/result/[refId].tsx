import { useRouter } from "next/router";
import { GroupResult } from "../../components/GroupResult";
import { LoadingPage } from "../../components/LoadingPage";
import { TranscriberHead } from "../../components/TranscriberHead";
import { TranscriptionResult } from "../../components/TranscriptionResult";

export default function TranscriptionResultPage() {
  const router = useRouter();
  const refId = router.query.refId as string;
  if (!router.isReady) {
    return <LoadingPage />;
  }
  if (refId.startsWith("gr-")) {
    return <GroupResult groupID={refId} />;
  } else {
    return <TranscriptionResult transcriptionID={refId} />;
  }
}
