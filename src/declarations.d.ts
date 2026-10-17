declare module "tailwind-merge" {
  export function twMerge(...classLists: (string | undefined | null | false)[]): string;
}

declare module "react-hook-form" {
  import * as React from "react";
  export type FieldValues = Record<string, any>;
  export type FieldPath<TFieldValues extends FieldValues = FieldValues> = string;
  export type ControllerProps<
    TFieldValues extends FieldValues = FieldValues,
    TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
  > = {
    name: TName;
    control?: any;
    render: (props: { field: any; fieldState: any; formState: any }) => React.ReactElement;
    defaultValue?: any;
    rules?: any;
    shouldUnregister?: boolean;
  };
  export const Controller: React.FC<ControllerProps<any, any>>;
  export const FormProvider: React.FC<{ children?: React.ReactNode; [key: string]: any }>;
  export function useFormContext(): any;
  export function useForm<TFieldValues extends FieldValues = FieldValues>(props?: any): any;
  export type UseFormReturn<TFieldValues extends FieldValues = FieldValues> = any;
}
