# Next.js Patterns Reference

Next.js 14+ App Router best practices and patterns.

---

## App Router Fundamentals

### File-Based Routing

```
app/
├── layout.tsx          # Root layout
├── page.tsx            # Home page (/)
├── loading.tsx         # Loading UI
├── error.tsx           # Error UI
├── not-found.tsx       # 404 page
├── dashboard/
│   ├── layout.tsx      # Dashboard layout
│   ├── page.tsx        # /dashboard
│   └── settings/
│       └── page.tsx    # /dashboard/settings
├── blog/
│   ├── page.tsx        # /blog
│   └── [slug]/
│       └── page.tsx    # /blog/:slug (dynamic)
└── api/
    └── users/
        └── route.ts    # API route
```

### Server Components (Default)

```tsx
// app/users/page.tsx - Server Component by default
import { db } from '@/lib/db';

// Async component - fetches data on server
export default async function UsersPage() {
  // Direct database access - no API needed
  const users = await db.user.findMany();

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users.map((user) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

### Client Components

```tsx
'use client';

import { useState } from 'react';

// Interactive components need 'use client'
export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

---

## Data Fetching Patterns

### Server-Side Data Fetching

```tsx
// Fetch with caching options
async function getUser(id: string) {
  const res = await fetch(`https://api.example.com/users/${id}`, {
    // Cache options
    cache: 'force-cache',     // Default - cache indefinitely
    // cache: 'no-store',     // Never cache (dynamic)
    // next: { revalidate: 60 }, // Revalidate every 60 seconds
  });

  if (!res.ok) throw new Error('Failed to fetch user');
  return res.json();
}

export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await getUser(params.id);
  return <UserProfile user={user} />;
}
```

### Parallel Data Fetching

```tsx
export default async function Dashboard() {
  // Fetch in parallel - not waterfall
  const [user, posts, notifications] = await Promise.all([
    getUser(),
    getPosts(),
    getNotifications(),
  ]);

  return (
    <div>
      <UserHeader user={user} />
      <PostList posts={posts} />
      <NotificationBell count={notifications.length} />
    </div>
  );
}
```

### Streaming with Suspense

```tsx
import { Suspense } from 'react';

export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Streams in as data loads */}
      <Suspense fallback={<UserSkeleton />}>
        <UserProfile />
      </Suspense>

      <Suspense fallback={<PostsSkeleton />}>
        <RecentPosts />
      </Suspense>
    </div>
  );
}
```

---

## Server Actions

### Form Handling

```tsx
// app/actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { z } from 'zod';

const CreatePostSchema = z.object({
  title: z.string().min(1).max(100),
  content: z.string().min(1),
});

export async function createPost(formData: FormData) {
  // Validate input
  const validated = CreatePostSchema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  });

  if (!validated.success) {
    return { error: validated.error.flatten().fieldErrors };
  }

  // Save to database
  await db.post.create({
    data: validated.data,
  });

  // Revalidate and redirect
  revalidatePath('/posts');
  redirect('/posts');
}
```

```tsx
// app/posts/new/page.tsx
import { createPost } from '../actions';

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit">Create Post</button>
    </form>
  );
}
```

### With useFormState

```tsx
'use client';

import { useFormState, useFormStatus } from 'react-dom';
import { createPost } from '../actions';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create Post'}
    </button>
  );
}

export function CreatePostForm() {
  const [state, formAction] = useFormState(createPost, { error: null });

  return (
    <form action={formAction}>
      <input name="title" placeholder="Title" />
      {state.error?.title && <p className="error">{state.error.title}</p>}

      <textarea name="content" placeholder="Content" />
      {state.error?.content && <p className="error">{state.error.content}</p>}

      <SubmitButton />
    </form>
  );
}
```

---

## Layout Patterns

### Root Layout

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: {
    template: '%s | My App',
    default: 'My App',
  },
  description: 'My awesome application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <Header />
          <main>{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
```

### Nested Layouts

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      <Sidebar />
      <div className="dashboard-content">{children}</div>
    </div>
  );
}
```

---

## Metadata & SEO

### Static Metadata

```tsx
// app/about/page.tsx
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About Us',
  description: 'Learn about our company',
  openGraph: {
    title: 'About Us',
    description: 'Learn about our company',
    images: ['/og-about.png'],
  },
};

export default function AboutPage() {
  return <div>About content</div>;
}
```

### Dynamic Metadata

```tsx
// app/blog/[slug]/page.tsx
import { Metadata } from 'next';

type Props = {
  params: { slug: string };
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = await getPost(params.slug);

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage],
    },
  };
}

export default async function BlogPost({ params }: Props) {
  const post = await getPost(params.slug);
  return <Article post={post} />;
}
```

---

## Route Handlers (API Routes)

```tsx
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const page = searchParams.get('page') ?? '1';

  const users = await db.user.findMany({
    skip: (parseInt(page) - 1) * 10,
    take: 10,
  });

  return NextResponse.json(users);
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  const user = await db.user.create({
    data: body,
  });

  return NextResponse.json(user, { status: 201 });
}
```

### Dynamic Route Handlers

```tsx
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';

type Params = { params: { id: string } };

export async function GET(request: NextRequest, { params }: Params) {
  const user = await db.user.findUnique({
    where: { id: params.id },
  });

  if (!user) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }

  return NextResponse.json(user);
}
```

---

## Middleware

```tsx
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Check authentication
  const token = request.cookies.get('token');

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Add headers
  const response = NextResponse.next();
  response.headers.set('x-custom-header', 'value');

  return response;
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
};
```

---

## Performance Optimizations

### Image Optimization

```tsx
import Image from 'next/image';

export function Hero() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero image"
      width={1200}
      height={600}
      priority // Preload for LCP
      placeholder="blur"
      blurDataURL="data:image/..."
    />
  );
}
```

### Font Optimization

```tsx
import { Inter, Roboto_Mono } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto-mono',
});

export default function RootLayout({ children }) {
  return (
    <html className={`${inter.variable} ${robotoMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

### Dynamic Imports

```tsx
import dynamic from 'next/dynamic';

// Client-side only component
const Chart = dynamic(() => import('@/components/Chart'), {
  ssr: false,
  loading: () => <ChartSkeleton />,
});

// Heavy component - load on demand
const RichTextEditor = dynamic(() => import('@/components/RichTextEditor'), {
  loading: () => <EditorSkeleton />,
});
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| 'use client' at top level | Opts out of Server Components | Use 'use client' only where needed |
| Fetching in useEffect | Double fetching, no SSR | Fetch in Server Components |
| Large client bundles | Slow initial load | Keep interactive code minimal |
| Missing loading.tsx | Poor loading UX | Add loading states |
| Not using Image | Unoptimized images | Use next/image |
| Client-side redirects | Slow, poor SEO | Use redirect() in server code |
