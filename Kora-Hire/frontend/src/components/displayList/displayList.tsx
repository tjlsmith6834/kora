import React, { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import "./displayList.css";
import VerticalDisplay from "../verticalDisplay/verticalDisplay";
import SmallButton from "../smallButton/smallButton";

interface CardListProps {
  children: React.ReactNode;
  emptyText?: string;
  /** Scroll to the very top of the page on page change (default: true) */
  scrollToTop?: boolean;
  /** Smooth scroll behavior (default: true) */
  smooth?: boolean;
}

const ITEMS_PER_PAGE = 15;

const DisplayList: React.FC<CardListProps> = ({
  children,
  emptyText,
  scrollToTop = true,
  smooth = true,
}) => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Get page from URL (default 1)
  const pageParam = searchParams.get("page");
  const page = pageParam ? parseInt(pageParam, 10) || 1 : 1;

  const totalItems = React.Children.count(children);
  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

  // Slice children for this page
  const start = (page - 1) * ITEMS_PER_PAGE;
  const end = start + ITEMS_PER_PAGE;
  const paginatedChildren = React.Children.toArray(children).slice(start, end);

  // Scroll to top of the window when page changes
  useEffect(() => {
    if (!scrollToTop) return;
    const behavior: ScrollBehavior = smooth ? "smooth" : "auto";
    window.scrollTo({ top: 0, behavior });
  }, [page, scrollToTop, smooth]);

  const goToPage = (newPage: number) => {
    if (newPage < 1 || newPage > totalPages) return;
    setSearchParams({ page: String(newPage) });
  };

  return (
    <div className="list-wrapper">
      <VerticalDisplay gap={"var(--spacing-md)"}>
        {totalItems === 0 && emptyText && (
          <h3 className="card-list-empty">{emptyText}</h3>
        )}
        {paginatedChildren.map((child, idx) => (
          <div key={idx} style={{ width: "100%", height: "100%" }}>
            {child}
          </div>
        ))}
      </VerticalDisplay>

      {totalPages > 1 && (
        <div className="pagination">
          <SmallButton
              onClick={() => goToPage(page - 1)}
              disabled={page <= 1}
              variant={"tertiary"}
              noBorder={false}
              symbol={false}
          >
            &lt; Prev
          </SmallButton>
          <span>
            Page {page} of {totalPages}
          </span>
          <SmallButton
              onClick={() => goToPage(page + 1)}
              disabled={page >= totalPages}
              variant={"tertiary"}
              noBorder={false}
              symbol={false}
          >
            Next &gt;
          </SmallButton>
        </div>
      )}
    </div>
  );
};

export default DisplayList;