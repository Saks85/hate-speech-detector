"use client";

import React from "react"
import { getLabelVariant, formatLabel } from "@/lib/utils";
import { useEffect, useState, useCallback } from "react";
import {
  BarChart3,
  MessageSquare,
  RefreshCw,
  Trash2,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import {
  getDashboardStats,
  getFeedbackList,
  deleteFeedback,
  triggerRetrain,
  type DashboardStats,
  type FeedbackItem,
} from "@/lib/api";

function StatsCard({
  title,
  value,
  icon: Icon,
  description,
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  description?: string;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}


export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [isLoadingStats, setIsLoadingStats] = useState(true);
  const [isLoadingFeedback, setIsLoadingFeedback] = useState(true);
  const [isRetraining, setIsRetraining] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const { toast } = useToast();

  const fetchStats = useCallback(async () => {
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch {
      toast({
        title: "Error",
        description: "Failed to load dashboard statistics",
        variant: "destructive",
      });
    } finally {
      setIsLoadingStats(false);
    }
  }, [toast]);

  const fetchFeedback = useCallback(async () => {
    try {
      const data = await getFeedbackList(100);
      setFeedback(data);
    } catch {
      toast({
        title: "Error",
        description: "Failed to load feedback list",
        variant: "destructive",
      });
    } finally {
      setIsLoadingFeedback(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchStats();
    fetchFeedback();
  }, [fetchStats, fetchFeedback]);

  const handleRetrain = async () => {
    setIsRetraining(true);
    try {
      const res = await triggerRetrain();

      toast({
        title: "Retraining Started",
        description: `New model version: ${res.new_version}`,
      });
    } catch {
      toast({
        title: "Error",
        description: "Failed to start retraining",
        variant: "destructive",
      });
    } finally {
      setIsRetraining(false);
    }
  };

  const handleDeleteFeedback = async (id: number) => {
    setDeletingId(id);
    try {
      await deleteFeedback(id);
      setFeedback((prev) => prev.filter((item) => item.id !== id));
      toast({
        title: "Deleted",
        description: "Feedback item has been removed",
      });
      fetchStats(); // Refresh stats after deletion
    } catch {
      toast({
        title: "Error",
        description: "Failed to delete feedback",
        variant: "destructive",
      });
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
            <p className="text-muted-foreground">
              Monitor API usage and manage user feedback
            </p>
          </div>
          <Button onClick={handleRetrain} disabled={isRetraining}>
            {isRetraining ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Retraining...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Trigger Retraining
              </>
            )}
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {isLoadingStats ? (
            <>
              {[1, 2, 3].map((i) => (
                <Card key={i} className="animate-pulse">
                  <CardHeader className="space-y-2 pb-2">
                    <div className="h-4 w-24 rounded bg-muted" />
                  </CardHeader>
                  <CardContent>
                    <div className="h-8 w-16 rounded bg-muted" />
                  </CardContent>
                </Card>
              ))}
            </>
          ) : stats ? (
            <>
              <StatsCard
                title="Total Feedback"
                value={stats.total_feedback.toLocaleString()}
                icon={MessageSquare}
                description="Total user feedback collected"
              />
              <StatsCard
                title="Model Errors"
                value={stats.model_errors.toLocaleString()}
                icon={AlertCircle}
                description="Incorrect model predictions"
              />
              <StatsCard
                title="Overrides"
                value={stats.overrides.toLocaleString()}
                icon={BarChart3}
                description="Manual label overrides"
              />
            </>
          ) : (
            <p className="col-span-full text-center text-muted-foreground">
              Unable to load statistics
            </p>
          )}
        </div>

        {/* Feedback Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-chart-1" />
              Recent Feedback
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingFeedback ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : feedback.length === 0 ? (
              <div className="py-12 text-center">
                <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground/50" />
                <p className="mt-2 text-muted-foreground">No feedback yet</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="min-w-[200px]">
                        Original Text
                      </TableHead>
                      <TableHead>Model Prediction</TableHead>
                      <TableHead>User Correction</TableHead>
                      <TableHead className="min-w-[150px]">Confidence</TableHead>
                      <TableHead className="w-[80px]">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {feedback.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="max-w-[250px] truncate font-mono text-sm">
                          {item.text}
                        </TableCell>
                        <TableCell>
                          <Badge variant={getLabelVariant(item.model_label)}>
                            {formatLabel(item.model_label)}
                          </Badge>
                        </TableCell>
                        <TableCell> 
                          {item.correct_label ? (
                            <Badge variant={getLabelVariant(item.correct_label)}>
                              {formatLabel(item.correct_label)}
                            </Badge>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          Confidence: {item.confidence.toFixed(3)}
                        </TableCell>
                        <TableCell>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon"
                                disabled={deletingId === item.id}
                              >
                                {deletingId === item.id ? (
                                  <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                  <Trash2 className="h-4 w-4 text-destructive" />
                                )}
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>
                                  Delete Feedback
                                </AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to delete this feedback
                                  item? This action cannot be undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => handleDeleteFeedback(item.id)}
                                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                >
                                  Delete
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
