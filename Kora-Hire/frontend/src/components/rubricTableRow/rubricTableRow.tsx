import React, { useState } from "react";
import RubricTableCriteriaList from "../rubricTableCriteriaList/rubricTableCriteriaList";
import SmallButton from "../smallButton/smallButton";
import { RubricCategory } from "../../types/job";

interface RubricTableRowProps {
  category: RubricCategory;
  editable: boolean;
  onChange: (updated: RubricCategory) => void;
  onRemove: () => void;
}

export default function RubricTableRow({
  category,
  editable,
  onChange,
  onRemove,
}: RubricTableRowProps) {
  const [isExpanded, setExpanded] = useState(false);

  const handleField = (key: keyof Omit<RubricCategory, "criteria">, val: any) =>
    onChange({ ...category, [key]: key === "weight" ? parseFloat(val) : val });

  return (
    <>
      <tr>
        <td>
          {editable ? (
            <input
              value={category.category}
              onChange={(e) => handleField("category", e.target.value)}
            />
          ) : (
            category.category
          )}
        </td>
        <td className={!editable ? "center-cell" : undefined}>
          {editable ? (
            <input className="weight-input"
              type="number"
              value={category.weight}
              min={1}
              max={5}
              onChange={(e) => handleField("weight", e.target.value)}
            />
          ) : (
            category.weight
          )}
        </td>
        <td>
          {editable ? (
            <textarea
              value={category.focus}
              onChange={(e) => handleField("focus", e.target.value)}
            />
          ) : (
            category.focus
          )}
        </td>
        <td className="center-cell">
          <span className="center-wrap">
            <SmallButton
                onClick={() => setExpanded((x) => !x)}
                symbol={true}
            >
              {!isExpanded ? "⋯" : "-"}
            </SmallButton>
          </span>
        </td>
        {editable && (
          <td className="center-cell">
            <span className="center-wrap">
              <SmallButton
                  onClick={onRemove}
                  variant={"secondary"}
                  symbol={true}
              >
                x
              </SmallButton>
            </span>
          </td>
        )}
      </tr>

      {isExpanded && (
        <tr className="expanded-row">
          <td colSpan={editable ? 5 : 4}>
            <RubricTableCriteriaList
              criteria={category.criteria}
              editable={editable}
              onChange={(newCriteria) =>
                onChange({ ...category, criteria: newCriteria })
              }
            />
          </td>
        </tr>
      )}
    </>
  );
}