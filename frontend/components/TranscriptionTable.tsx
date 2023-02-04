import {
  TableContainer,
  Table,
  Thead,
  Tr,
  Th,
  Tbody,
  Td,
  Badge,
} from "@chakra-ui/react";
import Link from "next/link";

export const TranscriptionTable = ({
  transcriptions,
}: {
  transcriptions: {
    token: string;
    link: string;
    summary: string;
    improvement_failed: boolean;
    transcribe_failed: boolean;
  }[];
}) => {
  const getStatusBadge = (transcription: {
    summary: string;
    improvement_failed: boolean;
    transcribe_failed: boolean;
  }) => {
    if (transcription.summary) {
      return <Badge colorScheme="green">Complete</Badge>;
    } else {
      if (transcription.improvement_failed || transcription.transcribe_failed) {
        return <Badge colorScheme="red">Error</Badge>;
      } else {
        return <Badge colorScheme="yellow">In progress</Badge>;
      }
    }
  };

  return (
    <TableContainer>
      <Table variant="unstyled">
        <Thead>
          <Tr>
            <Th style={{ width: "100%" }}>Video link</Th>
            <Th>Transcription link</Th>
            <Th>Status</Th>
          </Tr>
        </Thead>
        <Tbody>
          {transcriptions.map((transcription) => {
            return (
              <Tr key={transcription.token}>
                <Td>
                  <Link href={transcription.link}>{transcription.link}</Link>
                </Td>
                <Td>
                  <Link href={`/result/${transcription.token}`}>Link</Link>
                </Td>
                <Td>{getStatusBadge(transcription)}</Td>
              </Tr>
            );
          })}
        </Tbody>
      </Table>
    </TableContainer>
  );
};
