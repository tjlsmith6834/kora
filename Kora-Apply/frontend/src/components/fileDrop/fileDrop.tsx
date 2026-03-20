import React, {useCallback, useState} from "react";
import { useDropzone } from "react-dropzone";
import "./fileDrop.css";

interface FileDropProps {
    onFileSelect?: (file: File | null) => void;
    dropPrompt?: string;
    draggingPrompt?: string;
}

const FileDrop: React.FC<FileDropProps> = ({
       onFileSelect,
       dropPrompt,
       draggingPrompt
    }) => {

    const [file, setFile] = useState<File | null>(null);

    const fileTitle = React.useMemo(() => file ? file.name : "", [file]);

    const handleDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            const selectedFile = acceptedFiles[0];
            setFile(selectedFile);
            onFileSelect?.(selectedFile);
        }
    }, [onFileSelect]);

    const handleRemoveFile = () => {
        setFile(null);
        onFileSelect?.(null);
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        multiple: false,
        onDrop: handleDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
        }
    });

    return (
        <>
            <style>
                {`
                    .file-zone {
                        width: 100%;
                        margin: 0;
                        margin-bottom: var(--spacing-sm);
                        cursor: pointer;
                    }
                    
                    .file-zone p{
                        margin:0;
                    }
                    
                    .drop-zone {
                        border: var(--file-drop-border-neutral);
                        border-radius: var(--radius-sm);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        text-align: center;
                        padding: var(--spacing-md);
                        min-height: 4rem;
                        background-color: var(--color-card-background);
                        transition: background-color 0.3s ease-in-out;
                    }
                    
                    .drop-zone:hover {
                        background-color: var(--color-file-hover-add);
                        border-color: var(--color-file-drop-border-hover-add);
                    }
                    
                    .drop-zone.dragging {
                        background-color: var(--color-file-hover-add);
                        border-color: var(--color-file-drop-border-hover-add);
                    }
                    
                    .uploaded-file-wrapper{
                        border-radius: var(--radius-sm);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        text-align: center;
                        padding: var(--spacing-md);
                        min-height: 4rem;
                        background-color: var(--color-file-added);
                        transition: background-color 0.2s ease-in-out;
                    }
                    
                    .uploaded-file-wrapper:hover {
                        background-color: var(--color-file-hover-remove); /* Light red (Bootstrap danger color) */
                    }
                    
                    .file-title{
                        font-weight: bold;
                        margin: 0;
                    }
                `}
            </style>
            <div className="file-zone">
                {!fileTitle && (
                    <div {...getRootProps()} className={`drop-zone ${isDragActive ? "dragging" : ""}`}>
                        <input {...getInputProps()} />
                        {isDragActive ? (
                            <p>{draggingPrompt || "Drop the file here..."}</p>
                        ) : (
                            <p>
                                {dropPrompt || "Drop your file here, or click to select one."}
                                <br />
                                (PDF and Docx only please)
                            </p>
                        )}
                    </div>
                )}

                {fileTitle && (
                    <div className="uploaded-file-wrapper" onClick={handleRemoveFile}>
                        <p>
                            <span className="file-title">{fileTitle}</span>
                        </p>
                    </div>
                )}
            </div>
        </>
    );
};

export default FileDrop;