import React from 'react';
import Filters from './MovieFilters';
import { useDisclosure } from '@mantine/hooks';
import { Drawer, Button } from '@mantine/core';
import { IconAdjustmentsHorizontal } from '@tabler/icons-react';

function FilterDrawer({ filters, setFilters, ordering, setOrdering }) {
  const [opened, { open, close }] = useDisclosure(false);

  return (
    <>
      {/* Filter Button at the top-left */}
      <Button
        onClick={open}
        className="fixed top-4 left-4 z-20 p-2 px-4 border border-gray-700 rounded-lg bg-white text-black hover:bg-gray-100"
        variant="filled"
      >
        <span className="flex items-center">
          <IconAdjustmentsHorizontal className="h-5 w-5 mr-2" />
          <span className="font-medium">Filters</span>
        </span>
      </Button>

      {/* Mantine Drawer with black background */}
      <Drawer
        offset={8}
        radius="md"
        opened={opened}
        onClose={close}
        size="md"
        position="left"
        withCloseButton={false}
        padding={0}
        styles={{
          content: { backgroundColor: 'black' },
          header: { backgroundClip: 'black' },
        }}
      >
        <Filters filters={filters} setFilters={setFilters} ordering={ordering} setOrdering={setOrdering} />
      </Drawer>
    </>
  );
}

export default FilterDrawer;