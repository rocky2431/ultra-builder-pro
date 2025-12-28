import { Metadata } from 'next';
import { Suspense } from 'react';
import { notFound } from 'next/navigation';

// =============================================================================
// Metadata
// =============================================================================

export const metadata: Metadata = {
  title: 'Page Title',
  description: 'Page description for SEO',
  openGraph: {
    title: 'Page Title',
    description: 'Page description for social sharing',
    type: 'website',
  },
};

// Dynamic metadata example (uncomment if needed)
// type Props = { params: { slug: string } };
//
// export async function generateMetadata({ params }: Props): Promise<Metadata> {
//   const data = await fetchData(params.slug);
//
//   return {
//     title: data.title,
//     description: data.description,
//   };
// }

// =============================================================================
// Static Generation (optional)
// =============================================================================

// For dynamic routes, generate static params
// export async function generateStaticParams() {
//   const items = await fetchItems();
//   return items.map((item) => ({ slug: item.slug }));
// }

// =============================================================================
// Data Fetching
// =============================================================================

async function fetchPageData() {
  // Direct database access or API call
  // This runs on the server - no need for useEffect
  const response = await fetch('https://api.example.com/data', {
    next: { revalidate: 60 }, // ISR: revalidate every 60 seconds
    // cache: 'no-store', // For dynamic data
  });

  if (!response.ok) {
    throw new Error('Failed to fetch data');
  }

  return response.json();
}

// =============================================================================
// Loading Component (for Suspense)
// =============================================================================

function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-8 bg-gray-200 rounded w-1/3" />
      <div className="h-4 bg-gray-200 rounded w-2/3" />
      <div className="h-4 bg-gray-200 rounded w-1/2" />
    </div>
  );
}

// =============================================================================
// Async Data Component
// =============================================================================

async function PageContent() {
  const data = await fetchPageData();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">{data.title}</h1>
      <p className="text-gray-600">{data.description}</p>

      {/* Render data */}
      <ul className="space-y-2">
        {data.items?.map((item: { id: string; name: string }) => (
          <li key={item.id} className="p-4 bg-white rounded-lg shadow">
            {item.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

// =============================================================================
// Page Component (Server Component)
// =============================================================================

export default function Page() {
  return (
    <main className="container mx-auto px-4 py-8">
      {/* SEO-friendly heading structure */}
      <header className="mb-8">
        <h1 className="text-4xl font-bold">Page Title</h1>
        <p className="text-gray-600 mt-2">Page subtitle or description</p>
      </header>

      {/* Content with streaming */}
      <section>
        <Suspense fallback={<LoadingSkeleton />}>
          <PageContent />
        </Suspense>
      </section>

      {/* Additional sections */}
      <aside className="mt-12">
        <h2 className="text-2xl font-semibold mb-4">Related Content</h2>
        {/* Sidebar content */}
      </aside>
    </main>
  );
}

// =============================================================================
// Error Handling (create error.tsx in same folder)
// =============================================================================

// error.tsx
// 'use client';
//
// export default function Error({
//   error,
//   reset,
// }: {
//   error: Error & { digest?: string };
//   reset: () => void;
// }) {
//   return (
//     <div className="p-8 text-center">
//       <h2 className="text-2xl font-bold text-red-600">Something went wrong!</h2>
//       <p className="mt-2 text-gray-600">{error.message}</p>
//       <button
//         onClick={reset}
//         className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
//       >
//         Try again
//       </button>
//     </div>
//   );
// }

// =============================================================================
// Loading UI (create loading.tsx in same folder)
// =============================================================================

// loading.tsx
// export default function Loading() {
//   return (
//     <div className="container mx-auto px-4 py-8">
//       <div className="animate-pulse space-y-4">
//         <div className="h-10 bg-gray-200 rounded w-1/3" />
//         <div className="h-6 bg-gray-200 rounded w-2/3" />
//         <div className="grid grid-cols-3 gap-4 mt-8">
//           {[1, 2, 3].map((i) => (
//             <div key={i} className="h-40 bg-gray-200 rounded" />
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// }
