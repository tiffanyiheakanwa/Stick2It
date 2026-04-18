import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";

export function AISuggestionsSkeleton() {
  return (
    <div className="space-y-8">
      <div>
        <div className="mb-4 pb-2 border-b border-gray-200">
           <div className="flex items-center gap-2 mb-2">
             <Skeleton className="w-5 h-5 rounded-full" />
             <Skeleton className="h-6 w-48" />
           </div>
           <Skeleton className="h-4 w-64" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="border-2 flex flex-col justify-between border-gray-100 shadow-sm relative overflow-hidden h-40">
               <CardContent className="p-4 md:p-6 flex-1 flex flex-col">
                  <div className="flex items-start gap-3 md:gap-4 mb-4">
                     <Skeleton className="w-10 h-10 rounded-lg flex-shrink-0" />
                     <div className="flex-1 space-y-2">
                        <Skeleton className="h-5 w-3/4" />
                        <Skeleton className="h-4 w-1/2" />
                     </div>
                  </div>
                  <div className="mt-auto pt-4">
                     <Skeleton className="h-10 w-full rounded-md" />
                  </div>
               </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
