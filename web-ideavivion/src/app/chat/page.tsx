import {
  AuthTypeMetadata,
  getAuthTypeMetadataSS,
  getCurrentUserSS,
} from "@/lib/userSS";
import { redirect } from "next/navigation";
import { fetchSS } from "@/lib/utilsSS";
import { Connector, DocumentSet, Tag, User, ValidSources } from "@/lib/types";
import {
  BackendMessage,
  ChatSession,
  Message,
  RetrievalType,
} from "./interfaces";
import { unstable_noStore as noStore } from "next/cache";
import { Passist } from "../admin/passists/interfaces";
import { InstantSSRAutoRefresh } from "@/components/SSRAutoRefresh";
import { WelcomeModal } from "@/components/WelcomeModal";
import { ApiKeyModal } from "@/components/openai/ApiKeyModal";
import { cookies } from "next/headers";
import { DOCUMENT_SIDEBAR_WIDTH_COOKIE_NAME } from "@/components/resizable/contants";
import { passistComparator } from "../admin/passists/lib";
import { ChatLayout } from "./ChatPage";

export default async function Page({
  searchParams,
}: {
  searchParams: { [key: string]: string };
}) {
  noStore();

  const tasks = [
    getAuthTypeMetadataSS(),
    getCurrentUserSS(),
    fetchSS("/manage/connector"),
    fetchSS("/manage/document-set"),
    fetchSS("/passist?include_default=true"),
    fetchSS("/chat/get-user-chat-sessions"),
    fetchSS("/query/valid-tags"),
  ];

  // catch cases where the backend is completely unreachable here
  // without try / catch, will just raise an exception and the page
  // will not render
  let results: (User | Response | AuthTypeMetadata | null)[] = [
    null,
    null,
    null,
    null,
    null,
    null,
    null,
  ];
  try {
    results = await Promise.all(tasks);
  } catch (e) {
    console.log(`Some fetch failed for the main search page - ${e}`);
  }
  const authTypeMetadata = results[0] as AuthTypeMetadata | null;
  const user = results[1] as User | null;
  const connectorsResponse = results[2] as Response | null;
  const documentSetsResponse = results[3] as Response | null;
  const passistsResponse = results[4] as Response | null;
  const chatSessionsResponse = results[5] as Response | null;
  const tagsResponse = results[6] as Response | null;

  const authDisabled = authTypeMetadata?.authType === "disabled";
  if (!authDisabled && !user) {
    return redirect("/auth/login");
  }

  if (user && !user.is_verified && authTypeMetadata?.requiresVerification) {
    return redirect("/auth/waiting-on-verification");
  }

  let connectors: Connector<any>[] = [];
  if (connectorsResponse?.ok) {
    connectors = await connectorsResponse.json();
  } else {
    console.log(`Failed to fetch connectors - ${connectorsResponse?.status}`);
  }
  const availableSources: ValidSources[] = [];
  connectors.forEach((connector) => {
    if (!availableSources.includes(connector.source)) {
      availableSources.push(connector.source);
    }
  });

  let chatSessions: ChatSession[] = [];
  if (chatSessionsResponse?.ok) {
    chatSessions = (await chatSessionsResponse.json()).sessions;
  } else {
    console.log(
      `Failed to fetch chat sessions - ${chatSessionsResponse?.text()}`
    );
  }
  // Larger ID -> created later
  chatSessions.sort((a, b) => (a.id > b.id ? -1 : 1));

  let documentSets: DocumentSet[] = [];
  if (documentSetsResponse?.ok) {
    documentSets = await documentSetsResponse.json();
  } else {
    console.log(
      `Failed to fetch document sets - ${documentSetsResponse?.status}`
    );
  }

  let passists: Passist[] = [];
  if (passistsResponse?.ok) {
    passists = await passistsResponse.json();
  } else {
    console.log(`Failed to fetch passists - ${passistsResponse?.status}`);
  }
  // remove those marked as hidden by an admin
  passists = passists.filter((passist) => passist.is_visible);
  // sort them in priority order
  passists.sort(passistComparator);

  let tags: Tag[] = [];
  if (tagsResponse?.ok) {
    tags = (await tagsResponse.json()).tags;
  } else {
    console.log(`Failed to fetch tags - ${tagsResponse?.status}`);
  }

  const defaultPassistIdRaw = searchParams["passistId"];
  const defaultPassistId = defaultPassistIdRaw
    ? parseInt(defaultPassistIdRaw)
    : undefined;

  const documentSidebarCookieInitialWidth = cookies().get(
    DOCUMENT_SIDEBAR_WIDTH_COOKIE_NAME
  );
  const finalDocumentSidebarInitialWidth = documentSidebarCookieInitialWidth
    ? parseInt(documentSidebarCookieInitialWidth.value)
    : undefined;

  return (
    <>
      <InstantSSRAutoRefresh />
      <ApiKeyModal />

      {connectors.length === 0 && <WelcomeModal />}

      <ChatLayout
        user={user}
        chatSessions={chatSessions}
        availableSources={availableSources}
        availableDocumentSets={documentSets}
        availablePassists={passists}
        availableTags={tags}
        defaultSelectedPassistId={defaultPassistId}
        documentSidebarInitialWidth={finalDocumentSidebarInitialWidth}
      />
    </>
  );
}
