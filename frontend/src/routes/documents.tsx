import { createFileRoute } from "@tanstack/react-router";
import { FileText, LoaderCircle, RefreshCw, Trash2, Upload, X } from "lucide-react";
import { useRef, useState } from "react";

import { AppLayout } from "@/components/AppLayout";
import { StatusBadge } from "@/components/StatusBadge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAuth } from "@/lib/auth/auth-context";
import { useDeleteDocument, useDocuments, useUploadDocument } from "@/lib/api/hooks";
import { ApiError } from "@/lib/api/types";

export const Route = createFileRoute("/documents")({
  head: () => ({
    meta: [
      { title: "Documents — PharmaChain Supply Copilot" },
      { name: "description", content: "Upload and manage RAG source documents." },
    ],
  }),
  component: DocumentsPage,
});

const MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024;

function DocumentsPage() {
  const { user } = useAuth();
  const permissions = user?.permissions ?? [];
  const canRead = permissions.includes("documents.read");
  const canUpload = permissions.includes("documents.upload");
  const canDelete = permissions.includes("documents.delete");
  const documentsQuery = useDocuments({ enabled: canRead });
  const uploadMutation = useUploadDocument();
  const deleteMutation = useDeleteDocument();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [message, setMessage] = useState<{ tone: "success" | "error"; text: string } | null>(null);
  const [documentToDelete, setDocumentToDelete] = useState<{ id: string; name: string } | null>(null);

  const isUploading = uploadMutation.isPending;
  const isDeleting = deleteMutation.isPending;

  function selectFile(file: File | undefined) {
    setMessage(null);
    if (!file) return;

    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setSelectedFile(null);
      setMessage({ tone: "error", text: "Choose a PDF document to upload." });
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setSelectedFile(null);
      setMessage({ tone: "error", text: "The selected file exceeds the 25 MB upload limit." });
      return;
    }

    setSelectedFile(file);
  }

  async function uploadDocument() {
    if (!selectedFile || isUploading) return;

    setMessage(null);
    try {
      const document = await uploadMutation.mutateAsync(selectedFile);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setMessage({ tone: "success", text: `Upload successful. ${document.original_filename} is ${document.status}.` });
      await documentsQuery.refetch();
    } catch (error) {
      setMessage({ tone: "error", text: getErrorMessage(error, "Unable to upload the document.") });
    }
  }

  async function deleteDocument() {
    if (!documentToDelete || isDeleting) return;

    try {
      await deleteMutation.mutateAsync(documentToDelete.id);
      setMessage({ tone: "success", text: "Document deleted." });
      setDocumentToDelete(null);
      await documentsQuery.refetch();
    } catch (error) {
      setMessage({ tone: "error", text: getErrorMessage(error, "Unable to delete the document.") });
      setDocumentToDelete(null);
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Manage PDF sources for the RAG knowledge base.</p>
          </div>
          {canRead && (
            <Button variant="outline" onClick={() => void documentsQuery.refetch()} disabled={documentsQuery.isFetching}>
              <RefreshCw className={`size-4 ${documentsQuery.isFetching ? "animate-spin" : ""}`} />
              {documentsQuery.isFetching ? "Refreshing..." : "Refresh"}
            </Button>
          )}
        </div>

        {message && (
          <div className={`rounded-lg border p-3 text-sm ${message.tone === "success" ? "border-success/30 bg-success/10 text-success" : "border-destructive/30 bg-destructive/10 text-destructive"}`}>
            {message.text}
          </div>
        )}

        {canUpload && (
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-primary/10 text-primary"><Upload className="size-5" /></span>
                <div>
                  <h2 className="font-semibold">Upload document</h2>
                  <p className="mt-1 text-sm text-muted-foreground">PDF files only, up to 25 MB. The backend validates every upload before ingestion.</p>
                </div>
              </div>
              <input ref={fileInputRef} className="sr-only" type="file" accept="application/pdf,.pdf" onChange={(event) => selectFile(event.target.files?.[0])} disabled={isUploading} />
              {!selectedFile ? (
                <button type="button" onClick={() => fileInputRef.current?.click()} disabled={isUploading} className="mt-5 flex w-full flex-col items-center rounded-lg border border-dashed border-border bg-muted/30 px-6 py-8 text-center transition-colors hover:bg-muted/50 disabled:cursor-not-allowed">
                  <FileText className="size-8 text-muted-foreground" />
                  <span className="mt-3 font-medium">Choose PDF document</span>
                  <span className="mt-1 text-sm text-muted-foreground">Select a PDF from your device</span>
                </button>
              ) : (
                <div className="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-muted/30 p-4">
                  <div className="flex min-w-0 items-center gap-3">
                    <FileText className="size-5 shrink-0 text-primary" />
                    <div className="min-w-0"><p className="truncate font-medium">{selectedFile.name}</p><p className="text-xs text-muted-foreground">{formatFileSize(selectedFile.size)}</p></div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="icon" onClick={() => { setSelectedFile(null); if (fileInputRef.current) fileInputRef.current.value = ""; }} disabled={isUploading} aria-label="Remove selected file"><X /></Button>
                    <Button onClick={() => void uploadDocument()} disabled={isUploading}>{isUploading ? <LoaderCircle className="animate-spin" /> : <Upload />} {isUploading ? "Uploading..." : "Upload"}</Button>
                  </div>
                </div>
              )}
              {isUploading && <div className="mt-4 space-y-2"><div className="flex justify-between text-sm text-muted-foreground"><span>Uploading and ingesting document...</span><span>Please wait</span></div><Progress value={70} /></div>}
            </CardContent>
          </Card>
        )}

        <Card className="overflow-hidden">
          <CardContent className="p-0 overflow-x-auto">
            <Table>
              <TableHeader><TableRow className="bg-muted/40 hover:bg-muted/40"><TableHead>Document</TableHead><TableHead>Status</TableHead><TableHead>Uploaded</TableHead><TableHead>Pages</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
              <TableBody>
                {!canRead ? <TableRow><TableCell colSpan={5} className="py-10 text-center text-muted-foreground">You do not have permission to view documents.</TableCell></TableRow> : documentsQuery.isLoading ? <TableRow><TableCell colSpan={5} className="py-10 text-center text-muted-foreground">Loading documents...</TableCell></TableRow> : documentsQuery.isError ? <TableRow><TableCell colSpan={5} className="py-10 text-center text-destructive">{getErrorMessage(documentsQuery.error, "Unable to load documents.")}</TableCell></TableRow> : (documentsQuery.data ?? []).length === 0 ? <TableRow><TableCell colSpan={5} className="py-10 text-center text-muted-foreground">No documents have been uploaded yet.</TableCell></TableRow> : (documentsQuery.data ?? []).map((document) => <TableRow key={document.id} className="hover:bg-muted/40"><TableCell><div className="font-medium">{document.original_filename}</div><div className="mt-1 text-xs text-muted-foreground">{formatFileSize(document.file_size)}{document.failure_reason ? ` · ${document.failure_reason}` : ""}</div></TableCell><TableCell><DocumentStatus status={document.status} /></TableCell><TableCell className="text-sm text-muted-foreground">{formatDate(document.uploaded_at)}</TableCell><TableCell>{document.page_count ?? "—"}</TableCell><TableCell className="text-right">{canDelete && <Button variant="ghost" size="sm" onClick={() => setDocumentToDelete({ id: document.id, name: document.original_filename })} disabled={isDeleting}><Trash2 className="text-destructive" /> Delete</Button>}</TableCell></TableRow>)}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
      <AlertDialog open={Boolean(documentToDelete)} onOpenChange={(open) => !open && setDocumentToDelete(null)}><AlertDialogContent><AlertDialogHeader><AlertDialogTitle>Delete document?</AlertDialogTitle><AlertDialogDescription>This permanently removes {documentToDelete?.name ?? "this document"} and its ingested chunks.</AlertDialogDescription></AlertDialogHeader><AlertDialogFooter><AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel><AlertDialogAction onClick={(event) => { event.preventDefault(); void deleteDocument(); }} disabled={isDeleting} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">{isDeleting ? "Deleting..." : "Delete document"}</AlertDialogAction></AlertDialogFooter></AlertDialogContent></AlertDialog>
    </AppLayout>
  );
}

function DocumentStatus({ status }: { status: string }) {
  const tone = status === "COMPLETED" || status === "READY" ? "success" : status === "FAILED" ? "destructive" : status === "PROCESSING" || status === "PENDING" ? "warning" : "muted";
  return <StatusBadge label={status} tone={tone} />;
}

function getErrorMessage(error: unknown, fallback: string) {
  if (error instanceof ApiError) {
    const detail = error.body?.detail;
    return Array.isArray(detail) ? detail.join(", ") : detail || error.body?.message || fallback;
  }
  return error instanceof Error && error.message ? error.message : fallback;
}

function formatFileSize(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value: string) { const date = new Date(value); return Number.isNaN(date.getTime()) ? value : date.toLocaleString(); }
