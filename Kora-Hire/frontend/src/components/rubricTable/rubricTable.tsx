// ==== RubricTable.tsx ====
import React from "react";
import RubricTableRow from "../rubricTableRow/rubricTableRow";
import SmallButton from "../smallButton/smallButton";
import { Rubric, RubricCategory } from "../../types/job";
import "./rubricTable.css";

interface RubricTableProps {
  rubric?: Rubric;
  editable?: boolean;
  onChange?: (updated: Rubric) => void;
}

export default function RubricTable({
  rubric,
  editable = false,
  onChange,
}: RubricTableProps) {
  const handleAddCategory = () => {
    const newCat: RubricCategory = {
      category_id: crypto.randomUUID(),  // Only
      category: "",
      weight: 0,
      focus: "",
      criteria: [""],
    };

    const nextCats = [...categories, newCat];

    onChange?.({ categories: nextCats });
  };
  const categories: RubricCategory[] = rubric?.categories ?? [];

  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>Category</th>
            <th className={!editable ? "center-cell" : undefined}>Weight</th>
            <th>Focus</th>
            <th className="center-cell">Criteria</th>
            {editable && <th className="center-cell">Remove</th>}
          </tr>
        </thead>
        <tbody>
          {categories.map((cat, idx) => (
              <RubricTableRow
                  key={cat.category_id}
                  category={cat}
                  editable={editable}
                  onChange={(updatedCat) => {
                      const newCats = [...categories];
                      newCats[idx] = updatedCat;
                      onChange?.({ categories: newCats });
                  }}
                  onRemove={() => {
                      const newCats = categories.filter((_, i) => i !== idx);
                      onChange?.({ categories: newCats });
                  }}
              />
          ))}

        </tbody>
      </table>
      {editable && (
        <SmallButton
            onClick={handleAddCategory}
            variant={"tertiary"}
            className="cat-button"
        >
          + Add Category
        </SmallButton>
      )}
    </div>
  );
}