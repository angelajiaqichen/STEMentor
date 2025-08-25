import React from 'react';

const Documents: React.FC = () => {
  return (
    <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8\">
      <div className=\"mb-8\">
        <h1 className=\"text-3xl font-bold text-gray-900\">Documents</h1>
        <p className=\"mt-2 text-gray-600\">
          Upload and manage your learning materials
        </p>
      </div>

      <div className=\"card\">
        <div className=\"text-center py-12\">
          <div className=\"text-gray-500 mb-4\">
            <svg className=\"mx-auto h-12 w-12\" fill=\"none\" stroke=\"currentColor\" viewBox=\"0 0 24 24\">
              <path strokeLinecap=\"round\" strokeLinejoin=\"round\" strokeWidth={2} d=\"M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z\" />
            </svg>
          </div>
          <h3 className=\"text-lg font-semibold text-gray-900 mb-2\">No documents yet</h3>
          <p className=\"text-gray-500 mb-6\">Upload your first document to get started with AI-powered learning.</p>
          <button className=\"btn btn-primary\">Upload Document</button>
        </div>
      </div>
    </div>
  );
};

export default Documents;
