import { useEffect, useState } from "react";
import { apiGet } from "../services/api";

type Article = {
  id: number;
  slug: string;
  title: string;
  summary?: string;
  category?: string;
};

type Props = {
  category?: string;
  query?: string;
};

export function KnowledgeSuggestions({ category, query }: Props) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (category) params.set("category", category);
        if (query) params.set("q", query);
        const data = await apiGet(`/api/knowledge-base?${params.toString()}`) as { items: Article[] };
        setArticles(data.items || []);
      } catch (err) {
        console.warn("Knowledge suggestions fallback:", err);
        setArticles([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [category, query]);

  if (loading) {
    return (
      <div className="knowledge-card">
        <div className="loading" style={{ margin: "0 auto" }} />
      </div>
    );
  }

  if (!articles.length) {
    return null;
  }

  return (
    <div className="knowledge-card">
      <div className="card-header">
        <h3 className="card-title">🔍 پیشنهادهای مرتبط</h3>
      </div>
      <div className="knowledge-list">
        {articles.map((article) => (
          <div key={article.id} className="knowledge-item">
            <div className="knowledge-item__category">{article.category || "عمومی"}</div>
            <div className="knowledge-item__title">{article.title}</div>
            {article.summary && <div className="knowledge-item__summary">{article.summary}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}

