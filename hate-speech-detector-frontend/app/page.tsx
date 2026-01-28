import { Header } from "@/components/header";
import { Analyzer } from "@/components/analyzer";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto max-w-3xl px-4 py-8">
        <div className="mb-8 space-y-2">
          <h1 className="text-3xl font-bold tracking-tight text-balance">
            Hate Speech Detection
          </h1>
          <p className="text-muted-foreground text-pretty">
            Analyze text to detect hate speech, offensive language, or normal
            content using our advanced classification model.
          </p>
        </div>
        <Analyzer />
      </main>
    </div>
  );
}
