import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import "./fileUploader.css";

interface FileUploaderProps {
    header?: string;
    isEditable?: boolean;
    onFileChange?: (file: File | null) => void;
    placeholderText?: string | null;
}

const FileUploader: React.FC<FileUploaderProps> = ({
    isEditable = true,
    onFileChange,
    placeholderText,
}) => {
    const [file, setFile] = useState<File | null>(null);
    const hasFile = !!file;
    const fileTitle = hasFile ? file.name : placeholderText || null;


    const onDrop = useCallback(
        (acceptedFiles: File[]) => {
            if (!isEditable) return;
            const newFile = acceptedFiles[0];
            setFile(newFile);
            onFileChange?.(newFile);
        },
        [isEditable, onFileChange]
    );

    const handleClick = () => {
        if (!isEditable) return;
        if (hasFile) {
            setFile(null);
            onFileChange?.(null);
        } else {
            open(); // manually trigger file dialog
        }
    };

    const { getInputProps, open, isDragActive } = useDropzone({
        onDrop,
        accept: {
            "application/pdf": [".pdf"],
            "application/msword": [".doc"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
        },
        noClick: true,
        noKeyboard: true,
        disabled: !isEditable,
    });

    const fileZoneClass = [
        "file-zone",
        hasFile ? "has-file" : "no-file",
        isEditable ? "clickable" : "readonly",
        isDragActive ? "dragging" : "",
    ]
    .filter(Boolean)
    .join(" ");

    return (
        <div className="card-section">
            <div
                className={fileZoneClass}
                onClick={handleClick}
            >
                {fileTitle && (
                    <p>
                        <span className="file-title">{fileTitle}</span>
                    </p>
                )}
                {!fileTitle && isEditable &&  (
                    <>
                        <input {...getInputProps()} />
                        <p>
                            {isDragActive
                            ? "Drop the file here..."
                            : "Drop your file here, or click to select one.\n(PDFs and Docs only please)"}
                        </p>
                    </>
                )}
                {!fileTitle && !isEditable && <p>No file selected</p>}

            </div>
        </div>
    );
};

export default FileUploader;