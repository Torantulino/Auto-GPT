import React from "react";
import { ExecutionMeta, GraphMeta } from "@/lib/autogpt-server-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import moment from "moment/moment";
import { FlowRunStatusBadge } from "@/components/monitor/FlowRunStatusBadge";

export const FlowRunsList: React.FC<{
  flows: GraphMeta[];
  executions: ExecutionMeta[];
  className?: string;
  selectedRun?: ExecutionMeta | null;
  onSelectRun: (r: ExecutionMeta) => void;
}> = ({ flows, executions, selectedRun, onSelectRun, className }) => (
  <Card className={className}>
    <CardHeader>
      <CardTitle>Runs</CardTitle>
    </CardHeader>
    <CardContent>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Agent</TableHead>
            <TableHead>Started</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Duration</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {executions.map((execution) => (
            <TableRow
              key={execution.execution_id}
              className="cursor-pointer"
              onClick={() => onSelectRun(execution)}
              data-state={selectedRun?.execution_id == execution.execution_id ? "selected" : null}
            >
              <TableCell>
                {flows.find((f) => f.id == execution.graph_id)!.name}
              </TableCell>
              <TableCell>{moment(execution.started_at).format("HH:mm")}</TableCell>
              <TableCell>
                <FlowRunStatusBadge status={execution.status} />
              </TableCell>
              <TableCell>{formatDuration(execution.duration)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </CardContent>
  </Card>
);

function formatDuration(seconds: number): string {
  return (
    (seconds < 100 ? seconds.toPrecision(2) : Math.round(seconds)).toString() +
    "s"
  );
}

export default FlowRunsList;
