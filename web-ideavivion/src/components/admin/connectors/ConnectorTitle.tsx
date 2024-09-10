// import { getSourceMetadata } from "@/lib/sources";
// import {
//   ConfluenceConfig,
//   GoogleDriveConfig,
//   Connector,

// } from "@/lib/types";
// import Link from "next/link";

// interface ConnectorTitleProps {
//   connector: Connector<any>;
//   ccPairId: number;
//   ccPairName: string | null | undefined;
//   isPublic?: boolean;
//   owner?: string;
//   isLink?: boolean;
//   showMetadata?: boolean;
// }

// export const ConnectorTitle = ({
//   connector,
//   ccPairId,
//   ccPairName,
//   owner,
//   isPublic = true,
//   isLink = true,
//   showMetadata = true,
// }: ConnectorTitleProps) => {
//   const sourceMetadata = getSourceMetadata(connector.source);

//   let additionalMetadata = new Map<string, string>();
//   if (connector.source === "confluence") {
//     const typedConnector = connector as Connector<ConfluenceConfig>;
//     additionalMetadata.set(
//       "Wiki URL",
//       typedConnector.connector_specific_config.wiki_page_url
//     );
//   }
//    else if (connector.source === "google_drive") {
//     const typedConnector = connector as Connector<GoogleDriveConfig>;
//     if (
//       typedConnector.connector_specific_config?.folder_paths &&
//       typedConnector.connector_specific_config?.folder_paths.length > 0
//     ) {
//       additionalMetadata.set(
//         "Folders",
//         typedConnector.connector_specific_config.folder_paths.join(", ")
//       );
//     }
//  const mainSectionClassName = "text-blue-500 flex w-fit";
//   const mainDisplay = (
//     <>
//       {sourceMetadata.icon({ size: 20 })}
//       <div className="ml-1 my-auto">
//         {ccPairName || sourceMetadata.displayName}
//       </div>
//     </>
//   );
//   return (
//     <div className="my-auto">
//       {isLink ? (
//         <Link
//           className={mainSectionClassName}
//           href={`/admin/connector/${ccPairId}`}
//         >
//           {mainDisplay}
//         </Link>
//       ) : (
//         <div className={mainSectionClassName}>{mainDisplay}</div>
//       )}
//       {showMetadata && additionalMetadata.size > 0 && (
//         <div className="text-xs mt-1">
//           {Array.from(additionalMetadata.entries()).map(([key, value]) => {
//             return (
//               <div key={key}>
//                 <i>{key}:</i> {value}
//               </div>
//             );
//           })}
//         </div>
//       )}
//     </div>
//   );
// };



import { getSourceMetadata } from "@/lib/sources";
import {
  ConfluenceConfig,
  Connector,
  GoogleDriveConfig,
} from "@/lib/types";
import Link from "next/link";

interface ConnectorTitleProps {
  connector: Connector<any>;
  ccPairId: number;
  ccPairName: string | null | undefined;
  isPublic?: boolean;
  owner?: string;
  isLink?: boolean;
  showMetadata?: boolean;
}

export const ConnectorTitle = ({
  connector,
  ccPairId,
  ccPairName,
  owner,
  isPublic = true,
  isLink = true,
  showMetadata = true,
}: ConnectorTitleProps) => {
  const sourceMetadata = getSourceMetadata(connector.source);

  let additionalMetadata = new Map<string, string>();
  if (connector.source === "confluence") {
    const typedConnector = connector as Connector<ConfluenceConfig>;
    additionalMetadata.set(
      "Wiki URL",
      typedConnector.connector_specific_config.wiki_page_url
    );
  } else if (connector.source === "google_drive") {
    const typedConnector = connector as Connector<GoogleDriveConfig>;
    if (
      typedConnector.connector_specific_config?.folder_paths &&
      typedConnector.connector_specific_config?.folder_paths.length > 0
    ) {
      additionalMetadata.set(
        "Folders",
        typedConnector.connector_specific_config.folder_paths.join(", ")
      );
    }
  }

  const mainSectionClassName = "text-blue-500 flex w-fit";
  const mainDisplay = (
    <>
      {sourceMetadata.icon({ size: 20 })}
      <div className="ml-1 my-auto">
        {ccPairName || sourceMetadata.displayName}
      </div>
    </>
  );
  return (
    <div className="my-auto">
      {isLink ? (
        <Link
          className={mainSectionClassName}
          href={`/admin/connector/${ccPairId}`}
        >
          {mainDisplay}
        </Link>
      ) : (
        <div className={mainSectionClassName}>{mainDisplay}</div>
      )}
      {showMetadata && additionalMetadata.size > 0 && (
        <div className="text-xs mt-1">
          {Array.from(additionalMetadata.entries()).map(([key, value]) => {
            return (
              <div key={key}>
                <i>{key}:</i> {value}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
