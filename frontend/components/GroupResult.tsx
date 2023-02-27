import { Heading, Spinner, Text } from "@chakra-ui/react";
import Link from "next/link";
import { useState, useEffect } from "react";
import { getGroupTranscriptions } from "../client/api-client";
import { LogoAndTitle } from "./LogoAndTitle";
import { TranscriberHead } from "./TranscriberHead";
import { TranscriptionTable } from "./TranscriptionTable";

export const GroupResult = ({ groupID }: { groupID: string }) => {
  const [transcriptions, setTranscriptions] = useState<any[]>([]);
  const [groupLink, setGroupLink] = useState<string>("");

  useEffect(() => {
    getGroupTranscriptions(groupID)
      .then((data) => {
        const group = data.group;
        setGroupLink(group.link);
        setTranscriptions(group.members.transcriptions);
      })
      .catch((err) => {
        console.error(err);
      });
  }, [groupID]);

  return (
    <>
      <TranscriberHead
        title={`Transcribe ${groupLink && `| ${groupLink}`}`}
        description={`A transcription and summary of the youtube video with link: ${groupLink}`}
      />
      <main>
        <LogoAndTitle />
        {transcriptions ? (
          <>
            <Heading size="xl" paddingBottom={5}>
              Transcriptions for playlist.
            </Heading>
            <Text fontSize={"xl"} marginBottom={5}>
              Playlist Link: <Link href={groupLink}>{groupLink}</Link>
            </Text>
            <TranscriptionTable
              transcriptions={transcriptions}
              showOnlySuccessful={false}
            />
          </>
        ) : (
          <Spinner />
        )}
      </main>
    </>
  );
};
